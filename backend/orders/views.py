from collections import defaultdict

from django.db.models import Count, Avg, Sum, Prefetch
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.db import transaction

from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view

from cart.cart import Cart
from cart.models import CartItem
from cart.serializers import (
    CartItemAuthenticatedSerializer,
    CartItemSerializer
)
from users.models import Address
from cards.models import Card, Transaction
from stores.models import Store

from . import serializers
from .models import Product, Order, OrderItem
from .permissions import IsCustomerOrAdminUser, IsCustomerOrSellerOrAdminUser
from .services import send_order_success_notifications


User = get_user_model()


class OrderCreateView(APIView):
    def get(self, request):
        # Получаем данные о корзине и пользователе для создания заказа
        user = request.user

        if user.is_authenticated:
            cart_items = CartItem.objects.prefetch_related(
                Prefetch('product', queryset=Product.objects.annotate(
                reviews_count=Count('reviews'),
                average_score=Avg('reviews__score'),
                total_ordered_quantity=Sum('ordered_products__quantity')
            ).prefetch_related('reviews', 'product_images'
            ).select_related('seller', 'cosplay_character__fandom'
            ).filter(is_active=True))).filter(user=user)
            
            if not cart_items:
                return Response({'error': 'Your cart is empty.'}, status=status.HTTP_400_BAD_REQUEST)
            
            cart_length = sum(item.quantity for item in cart_items)
            total_cart_price = sum(item.get_total_price() for item in cart_items)

            order_data = {
                'cart_length': cart_length,
                'cart_items': CartItemAuthenticatedSerializer(cart_items, many=True).data,
                'total_cart_price': total_cart_price,
                'name': user.first_name,
                'email': user.email,
                'phone_number': user.phone_number,
                'addresses': user.addresses.all(),
                'cards': user.cards.all(),
                }
            
        else:
            cart = Cart(request)
            if not cart:
                return Response({'error': 'Your cart is empty.'}, status=status.HTTP_400_BAD_REQUEST)
            cart_length = cart.__len__()
            cart_items = cart.get_cart_items()
            total_cart_price = cart.get_total_cart_price()
    
            order_data = {
                'cart_length': cart_length,
                'cart_items': CartItemSerializer(cart_items, many=True).data,
                'total_cart_price': total_cart_price,
                'name': '',
                'email': '',
                'phone_number': '',
                'addresses': '',
                'cards': '',
                }
        
        serializer = serializers.OrderCartSerializer(order_data)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @transaction.atomic
    def post(self, request):
        user = request.user
        # Валидация формы для авторизованного и неавторизованного пользователя
        if user.is_authenticated:
            serializer = serializers.OrderCreateAuthenticatedSerializer(data=request.data, 
                                                                        context={'request': request})
            user_addresses = user.addresses.all()
            user_cards = user.cards.all()
        else:
            serializer = serializers.OrderCreateSerializer(data=request.data)
            cart = Cart(request)
            session_cart_items = cart.get_cart_items()
            
        if serializer.is_valid():
            if user.is_authenticated:
                user_data = {
                    'name': user.first_name if user.first_name else serializer.validated_data.get('name'),
                    'email': user.email,
                    'phone_number': user.phone_number if user.phone_number else serializer.validated_data.get('phone_number'),
                    'address': serializer.validated_data.get('address'),
                    'card': serializer.validated_data.get('card'),
                }
            else:
                user_data = {
                    'name': serializer.validated_data.get('name'),
                    'email': serializer.validated_data.get('email'),
                    'phone_number': serializer.validated_data.get('phone_number'),
                    'address': serializer.validated_data.get('address'),
                    'card': serializer.validated_data.get('card'),
                }
            
                anonymous_card = Card.objects.create(user=None, card_number=user_data['card'])
                anonymous_address = Address.objects.create(user=None, address=user_data['address'])

            # Обновление данных пользователя
            authenticated_card = None
            authenticated_address = None

            if user.is_authenticated:
                if not user.first_name or not user.phone_number:
                    if not user.first_name:
                        user.first_name = user_data['name']
                    if not user.phone_number:
                        user.phone_number = user_data['phone_number']
                    user.save()

                if not user_cards:
                    authenticated_card = Card.objects.create(user=user, card_number=user_data['card'])
                if not user_addresses:
                    authenticated_address = Address.objects.create(user=user, address=user_data['address'])

            # Создание предметов заказа
            if user.is_authenticated:
                db_cart_items = CartItem.objects.filter(user=user).prefetch_related('product')

                if not db_cart_items:
                    return Response({'error': 'Your cart is empty.'}, status=status.HTTP_400_BAD_REQUEST)
                
                total_order_price = sum(db_cart_item.get_total_price() for db_cart_item in db_cart_items)
                
                # Создание заказа
                order = serializer.save(customer=user, 
                                        name=user_data['name'],
                                        phone_number=user_data['phone_number'],
                                        email=user_data['email'],
                                        card=authenticated_card if authenticated_card else user_data['card'],
                                        address=authenticated_address if authenticated_address else user_data['address'],
                                        total_order_price=total_order_price, 
                                        status=1)
                
                for db_cart_item in db_cart_items:
                    OrderItem.objects.create(order=order, 
                                             product=db_cart_item.product, 
                                             price=db_cart_item.product.get_real_price(), 
                                             quantity=db_cart_item.quantity,
                                             status=1)
                # Очистка корзины авторизованного пользователя
                db_cart_items.delete()

            else:
                if not session_cart_items:
                    return Response({'error': 'Your cart is empty.'}, status=status.HTTP_400_BAD_REQUEST)
                
                # Создание заказа
                order = serializer.save(customer=None, 
                                        card=anonymous_card,
                                        address=anonymous_address,
                                        total_order_price=cart.get_total_cart_price(), 
                                        status=1)
                
                for item in session_cart_items:
                    product_id = item['product'].id
                    product = get_object_or_404(
                        Product.objects.annotate(
                            reviews_count=Count('reviews'),
                            average_score=Avg('reviews__score'),
                            total_ordered_quantity=Sum('ordered_products__quantity')
                        ).prefetch_related('reviews', 'product_images'
                        ).select_related('seller', 'cosplay_character__fandom'
                        ), pk=product_id, is_active=True)
                    quantity = item['quantity']
                    price = item['price']

                    OrderItem.objects.create(order=order,
                                             product=product,
                                             quantity=quantity,
                                             price=price,
                                             status=1)    
                # Очистка сессионной корзины
                cart.clear()

            # Отправка SMS и Email об успешном оформлении заказа через Celery
            send_order_success_notifications(user, order)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({'message': 'Your order has been successfully created.'}, status=status.HTTP_201_CREATED)


class OrderListView(generics.ListAPIView):
    serializer_class = serializers.OrderListSerializer
    permission_classes = (IsAuthenticated,)
    
    def get_queryset(self):
        user = self.request.user
        return Order.objects.prefetch_related(
            Prefetch('order_items__product', queryset=Product.objects.annotate(
                reviews_count=Count('reviews'),
                average_score=Avg('reviews__score'),
                total_ordered_quantity=Sum('ordered_products__quantity')
                ).prefetch_related('reviews', 'product_images'
                ).select_related('seller', 'cosplay_character__fandom'))
            ).filter(customer=user)
    

class OrderDetailView(generics.RetrieveAPIView):
    serializer_class = serializers.OrderDetailSerializer
    permission_classes = (IsCustomerOrAdminUser,)
    queryset = Order.objects.prefetch_related(
        Prefetch('order_items__product', queryset=Product.objects.annotate(
            reviews_count=Count('reviews'),
            average_score=Avg('reviews__score'),
            total_ordered_quantity=Sum('ordered_products__quantity')
            ).prefetch_related('reviews', 'product_images'
            ).select_related('seller', 'cosplay_character__fandom'))
        ).select_related('card', 'address', 'customer').annotate(
            ordered_products_amount=Count('order_items'),
            total_order_items_quantity=Sum('order_items__quantity')).all()
    lookup_field = 'slug'
    

class OrderItemView(generics.RetrieveAPIView):
    serializer_class = serializers.OrderItemSerializer
    permission_classes = (IsCustomerOrSellerOrAdminUser,)
    queryset = OrderItem.objects.select_related('order__customer',
                                                'order__address',
                                                'order__card'
        ).prefetch_related(Prefetch('product', queryset=Product.objects.annotate(
            reviews_count=Count('reviews'),
            average_score=Avg('reviews__score'),
            total_ordered_quantity=Sum('ordered_products__quantity')
            ).prefetch_related('reviews', 'product_images',
            ).select_related('seller', 'cosplay_character__fandom'))).all()
    lookup_field = 'slug'
    

@api_view(['POST'])
@transaction.atomic
def create_order_payment(request, order_id):
    user = request.user
    main_store = Store.objects.get(id=1)

    order_queryset = Order.objects.prefetch_related(Prefetch(
        'order_items', 
        queryset=OrderItem.objects.select_related('product__seller'))
        ).select_related('card', 'customer')
    order = get_object_or_404(order_queryset, pk=order_id)

    if (order.customer and user.is_authenticated and user == order.customer) or not (order.customer and user.is_authenticated):
        card = order.card
        payment_amount = order.total_order_price

        if card.balance < payment_amount:
            return Response({'error': 'Insufficient funds on the card.'}, status=status.HTTP_400_BAD_REQUEST)
        
        Transaction.objects.create(card=card, transaction_type='Purchase', amount=payment_amount, related_order=order)
        card.balance -= payment_amount
        card.save()

        main_store_proceeds = 0
        other_stores_proceeds = defaultdict(int)

        for item in order.order_items.all():
            seller = item.product.seller
            comission = round(item.get_total_price() * 0.05)
            sale_proceeds = item.get_total_price() - comission

            if seller == main_store:
                main_store_proceeds += item.get_total_price()
            else:
                other_stores_proceeds[seller] += sale_proceeds 
                main_store_proceeds += comission

            Transaction.objects.create(transaction_type='Sale',
                                       related_order_item=item,
                                       related_seller=seller,
                                       amount=item.get_total_price())
            
            if seller != main_store:
                Transaction.objects.create(transaction_type='Comission',
                                           related_order_item=item,
                                           related_seller=seller,
                                           amount=comission)
            
            item_product = item.product

            if item_product.in_stock is not None:
                if item_product.in_stock > 0 and item_product.is_active:
                    item_product.in_stock -= item.quantity
                    item_product.save()
                else:
                    return Response({'error': 'Product is not available to purchase.'}, status=status.HTTP_400_BAD_REQUEST)

            item.status = 2
            item.save()

        if other_stores_proceeds:
            for store, proceeds in other_stores_proceeds.items():
                store.balance += proceeds
                store.save()

        main_store.balance += main_store_proceeds
        main_store.save()

        order.status = 2
        order.save()
    else:
        return Response({'error': 'You cannot pay for this order.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    
    return Response({'message': 'Order was paid successfully.'}, status=status.HTTP_200_OK)