from django.db import transaction
from django.http import JsonResponse
from django.db.models import Count, Avg, Q, Prefetch, Sum
from django.shortcuts import get_object_or_404

from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import ValidationError

from products.models import Product, Review, ProductImage
from orders.models import OrderItem, ORDER_ITEM_STATUS_CHOICES
from cards.models import Transaction
from products.serializers import ProductCreateSerializer, AnswerCreateSerializer
from common.serializers import StoreListSerializer

from .models import Store, Employee
from . import serializers
from . import permissions


class StoreCreateView(generics.CreateAPIView):
    serializer_class = serializers.StoreCreateSerializer
    permission_classes = (IsAuthenticated,)
    queryset = Store.objects.select_related('owner').all()

    @transaction.atomic
    def perform_create(self, serializer):
        user = self.request.user

        if Store.objects.filter(owner=user).exists():
            raise ValidationError("You cannot create more than 1 store.")
        
        store = serializer.save(owner=user)
        Employee.objects.create(user=user, store=store, is_admin=True, is_owner=True)


class StoreDetailPrivateView(generics.RetrieveUpdateAPIView):
    serializer_class = serializers.StoreDetailPrivateSerializer
    permission_classes = (permissions.IsOwnerOrStoreAdminOrAdminReadOnly,)
    queryset = Store.objects.select_related('owner').all()
    lookup_field = 'slug'


class StoreDeleteView(generics.DestroyAPIView):
    serializer_class = serializers.StoreDetailPrivateSerializer
    permission_classes = (permissions.IsOwnerOrAdminUser,)
    queryset = Store.objects.select_related('owner').all()
    lookup_field = 'slug'            


class StoreDetailPublicView(generics.RetrieveAPIView):
    serializer_class = serializers.StoreDetailPublicSerializer
    lookup_field = 'slug'
    queryset = Store.objects.prefetch_related(
        Prefetch(
            'store_products',
            queryset=Product.objects.select_related('seller', 'cosplay_character__fandom'
                ).prefetch_related('product_images').annotate(
                    reviews_count=Count('reviews'),
                    average_score=Avg('reviews__score'),
                    total_ordered_quantity=Sum('ordered_products__quantity')
                ).filter(is_active=True)
        )
        ).annotate(
            products_count=Count('store_products', filter=Q(store_products__is_active=True)),
            store_average_score=Avg('store_products__reviews__score')
        ).all()
    

class StoreListView(generics.ListAPIView):
    serializer_class = StoreListSerializer
    queryset = Store.objects.annotate(
        products_count=Count('store_products', filter=Q(store_products__is_active=True)),
        store_average_score=Avg('store_products__reviews__score')).all()


class StoreTransactionListView(generics.ListAPIView):
    permission_classes = (permissions.IsEmployee,)

    def get_queryset(self):
        store = self.store
        if store.is_admin_store:
            return Transaction.objects.select_related(
                'card__user', 'related_order_item__product__cosplay_character__fandom', 'related_seller'
                ).prefetch_related('related_order_item__product__product_images'
                ).filter(Q(related_seller=store) | Q(transaction_type="Comission")).order_by('-timestamp')
        else:
            return Transaction.objects.select_related(
                'card__user', 'related_order_item__product__cosplay_character__fandom', 'related_seller'
                ).prefetch_related('related_order_item__product__product_images'
                ).filter(related_seller=store).order_by('-timestamp')

    def get_serializer_class(self, *args, **kwargs):
        store = self.store
        if store.is_admin_store:
            return serializers.AdminStoreTransactionsListSerializer
        else:
            return serializers.StoreTransactionsListSerializer
        
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['store'] = self.store
        return context


class EmployeeCreateView(generics.CreateAPIView):
    serializer_class = serializers.EmployeeCreateSerializer
    permission_classes = (permissions.IsOwnerOrStoreAdmin,)

    def perform_create(self, serializer):
        store = self.store
        new_employee = serializer.save(store=store)


class EmployeeListView(generics.ListAPIView):
    serializer_class = serializers.EmployeeSerializer
    permission_classes = (permissions.IsEmployee,)

    def get_queryset(self):
        store = self.store
        return Employee.objects.select_related(
            'user', 'store').filter(store=store).order_by(
            '-is_owner', '-is_admin', 'hired_at')
    

class EmployeeDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = serializers.EmployeeSerializer
    permission_classes = (permissions.IsOwnerOrStoreAdminOrEmployeeReadOnly,)
    lookup_field = 'user__username'
    lookup_url_kwarg = 'username'

    def get_queryset(self):
        store = self.store
        return Employee.objects.select_related('user', 'store').filter(store=store)
    

class StoreOrderListView(generics.ListAPIView):
    serializer_class = serializers.StoreOrdersListSerializer
    permission_classes = (permissions.IsEmployee,)

    def get_queryset(self):
        store = self.store
        return OrderItem.objects.select_related(
            'product__cosplay_character__fandom',
            'product__seller', 'order__customer', 'order__address'
            ).prefetch_related('product__product_images'
            ).filter(product__seller=store).order_by('-created_at')


class StoreProductListView(generics.ListAPIView):
    serializer_class = serializers.StoreProductListSerializer
    permission_classes = (permissions.IsEmployee,)

    def get_queryset(self):
        store = self.store
        return Product.objects.select_related('cosplay_character__fandom', 'seller'
                ).prefetch_related('product_images').annotate(
                    reviews_count=Count('reviews', distinct=True),
                    average_score=Avg('reviews__score'),
                    total_ordered_quantity=Sum('ordered_products__quantity'),
                    total_orders=Count('ordered_products',),
                    total_orders_done=Count('ordered_products', filter=Q(ordered_products__status=5)),
                    total_orders_processing=Count('ordered_products', filter=Q(ordered_products__status__in=[1, 2, 3, 4])),
                    total_orders_cancelled=Count('ordered_products', filter=Q(ordered_products__status=0))
                ).filter(seller=store).order_by('-is_active', '-total_orders_processing', '-timestamp')
    

class StoreProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = serializers.StoreProductDetailSerializer
    permission_classes = (permissions.IsOwnerOrStoreAdminOrEmployeeRetrieveUpdateOnly,)
    lookup_field = 'slug'

    def get_queryset(self):
        store = self.store
        return Product.objects.select_related('cosplay_character__fandom', 'seller'
                ).prefetch_related('reviews__customer',
                                   'reviews__answers__seller', 
                                   'product_images',
                                   'ordered_products'
                ).annotate(
                    reviews_count=Count('reviews'),
                    average_score=Avg('reviews__score'),
                    total_orders=Count('ordered_products'),
                    total_ordered_quantity=Sum('ordered_products__quantity'),
                    total_orders_done=Count('ordered_products', filter=Q(ordered_products__status=5)),
                    total_orders_processing=Count('ordered_products', filter=Q(ordered_products__status__in=[1, 2, 3, 4])),
                    total_orders_cancelled=Count('ordered_products', filter=Q(ordered_products__status=0))
                ).filter(seller=store)
    
    def perform_update(self, serializer):
        instance = serializer.save()
        if instance.in_stock == 0:
            instance.is_active = False
        instance.save()
    

class ProductCreateView(generics.CreateAPIView):
    serializer_class = ProductCreateSerializer
    permission_classes = (permissions.IsEmployee,)

    @transaction.atomic
    def perform_create(self, serializer):
        store = self.store
        product = serializer.save(seller=store)

        if product.in_stock == 0:
            product.is_active = False
            product.save()

        product_images = serializer.validated_data.get('product_images', [])

        if product_images:
            for image in product_images:
                ProductImage.objects.create(product=product, image=image)
        else:
            ProductImage.objects.create(product=product)

    
class AnswerCreateView(generics.CreateAPIView):
    serializer_class = AnswerCreateSerializer
    permission_classes = (permissions.IsEmployee,)

    def perform_create(self, serializer):
        store = self.store

        review_id = self.kwargs['review_id']
        review = get_object_or_404(Review, pk=review_id, product__seller=store)

        answer = serializer.save(seller=store, review=review)


@api_view(['POST'])
@permission_classes([permissions.IsEmployee,])
@transaction.atomic
def update_order_status(request, slug, order_item_slug, new_status):
    store = get_object_or_404(Store, slug=slug)
    order_item = get_object_or_404(OrderItem, slug=order_item_slug, product__seller=store)

    try:
        new_status = int(new_status)
    except (ValueError, TypeError):
        return Response({'error': 'Invalid status value.'}, status=status.HTTP_400_BAD_REQUEST)

    if new_status not in [0, 2, 3, 4]:
        return Response({'error': 'Invalid status value.'}, status=status.HTTP_400_BAD_REQUEST)

    order_item.status = new_status
    order_item.save()

    order = order_item.order
    order_item_statuses = list(order.order_items.values_list('status', flat=True))

    status_counts = {status: order_item_statuses.count(str(status)) for status, _ in ORDER_ITEM_STATUS_CHOICES}

    if status_counts[0] == len(order_item_statuses):
        order.status = 0
    elif status_counts[1] > 0:
        order.status = 1
    elif status_counts[2] > 0:
        order.status = 2
    elif status_counts[3] > 0:
        order.status = 3
    elif status_counts[4] == (len(order_item_statuses) - status_counts[0]):
        order.status = 4

    order.save()

    return Response({'message': 'Order status updated successfully.'}, status=status.HTTP_200_OK)

