from .serializers import *
from .models import (Fandom, Character, Product, Review, Order,
                     OrderItem, Favorite, CreditCard,)
from .cart import Cart
from django.db.models import Count, Avg, Prefetch, Q
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
User = get_user_model()

    
# Create Views
class FandomCreateView(generics.CreateAPIView):
	serializer_class = CreateFandomSerializer
        

class CharacterCreateView(generics.CreateAPIView):
	serializer_class = CreateCharacterSerializer


class ProductCreateView(generics.CreateAPIView):
	serializer_class = CreateProductSerializer


class ReviewCreateView(generics.CreateAPIView):
	serializer_class = CreateReviewSerializer


class OrderCreateView(APIView):
    authentication_classes = [JWTAuthentication]

    def get_cart_items(self, request):
        cart = Cart(request)
        return cart.get_cart_items()

    def get(self, request):
        cart_items = self.get_cart_items(request)
        serializer = CartItemSerializer(cart_items, many=True)
        return Response({'cart_items': serializer.data})

    def post(self, request):
        if request.user.is_authenticated:
            serializer = CreateOrderAuthenticatedSerializer(data=request.data)
        else:
            serializer = CreateOrderSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        cart_items = self.get_cart_items(request)
        user = request.user
        order = serializer.save(customer=user if user.is_authenticated else None, status="Created")

        for item in cart_items:
            product_id = item['product'].id
            product = Product.objects.prefetch_related('seller', 'reviews').annotate(
                    reviews_count=Count('reviews'),
                    average_score=Avg('reviews__score')
                ).get(id=product_id)
            quantity = item['quantity']
            OrderItem.objects.create(order=order, product=product, quantity=quantity)

        cart = Cart(request)
        cart.clear()

        return Response({'message': 'Заказ успешно оформлен'}, status=status.HTTP_201_CREATED)



class CreditCardCreateView(generics.CreateAPIView):
	serializer_class = CreateCreditCardSerializer


# List Views
class UserListView(generics.ListAPIView):
    serializer_class = CustomUserSerializer
    queryset = User.objects.prefetch_related('groups', 'user_permissions').filter(is_active=True)


class InactiveUserListView(generics.ListAPIView):
    serializer_class = CustomUserSerializer
    queryset = User.objects.prefetch_related('groups', 'user_permissions').filter(is_active=False)


class FandomListView(generics.ListAPIView):
    serializer_class = FandomSerializer
    queryset = Fandom.objects.prefetch_related(
        Prefetch('characters__products', queryset=Product.objects.filter(is_active=True))) \
            .annotate(characters_count=Count('characters')).all()


class CharacterListView(generics.ListAPIView):
    serializer_class = CharacterDetailSerializer
    queryset = Character.objects.select_related('fandom') \
        .annotate(products_count=Count('products', filter=Q(products__is_active=True))).all()


class CharacterProductListView(generics.RetrieveAPIView):
    serializer_class = CharacterProductSerializer
    queryset = Character.objects.select_related('fandom').prefetch_related(
        Prefetch('products', queryset=Product.objects.filter(is_active=True).annotate(
            reviews_count=Count('reviews'),
            average_score=Avg('reviews__score')
        ).prefetch_related('seller', 'reviews'))
        ).annotate(products_count=Count('products', filter=Q(products__is_active=True)))


class FandomCharacterListView(generics.RetrieveAPIView):
    serializer_class = FandomCharacterSerializer
    queryset = Fandom.objects.prefetch_related(
        Prefetch('characters', queryset=Character.objects \
        .annotate(products_count=Count('products', filter=Q(products__is_active=True))))) \
        .annotate(characters_count=Count('characters')).all()
    

class FandomProductListView(generics.RetrieveAPIView):
    serializer_class = FandomProductSerializer
    queryset = Fandom.objects \
        .prefetch_related(Prefetch('characters', queryset=Character.objects.annotate(
            products_count=Count('products', filter=Q(products__is_active=True))
        ).prefetch_related(Prefetch('products', queryset=Product.objects.filter(is_active=True).annotate(
            reviews_count=Count('reviews'),
            average_score=Avg('reviews__score')
        ).prefetch_related('seller', 'reviews')))) 
        ).annotate(characters_count=Count('characters')).all()


class ProductListView(generics.ListAPIView):
    serializer_class = ProductSerializer
    queryset = Product.objects \
        .select_related('seller', 'cosplay_character__fandom').annotate(
            reviews_count=Count('reviews'),
            average_score=Avg('reviews__score')
            ).filter(is_active=True)


class OrderListView(generics.ListAPIView):
    serializer_class = OrderSerializer
    
    def get_queryset(self):
        pk = self.kwargs['pk']
        return Order.objects.filter(customer=pk)
    

class OrderItemView(generics.RetrieveAPIView):
    serializer_class = OrderItemSerializer
    queryset = OrderItem.objects.prefetch_related(Prefetch('product', queryset=Product.objects.annotate(
            reviews_count=Count('reviews'),
            average_score=Avg('reviews__score')
        ).prefetch_related('seller', 'reviews'))).all()


class CreditCardListView(generics.ListAPIView):
    serializer_class = CreditCardSerializer

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        return CreditCard.objects.filter(user=user_id)


class ReviewListView(generics.ListAPIView):
    serializer_class = ReviewSerializer

    def get_queryset(self):
        product_id = self.kwargs['product_id']
        return Review.objects \
            .select_related('product', 'customer').filter(product=product_id)


class FavoriteListView(generics.ListAPIView):
    serializer_class = FavoriteSerializer
    queryset = Favorite.objects.all()


# Detail Views
class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = UserDetailSerializer
    queryset = User.objects.prefetch_related('credit_cards').all()


class FandomDetailView(generics.RetrieveUpdateDestroyAPIView):
	serializer_class = FandomSerializer
	queryset = Fandom.objects.prefetch_related(
        Prefetch('characters__products', queryset=Product.objects.filter(is_active=True))
        ).annotate(characters_count=Count('characters')).all()
	

class CharacterDetailView(generics.RetrieveUpdateDestroyAPIView):
	serializer_class = CharacterDetailSerializer
	queryset = Character.objects.select_related('fandom') \
        .annotate(products_count=Count('products',
                                       filter=Q(products__is_active=True))).all()


class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProductDetailSerializer
    queryset = Product.objects.select_related('seller', 'cosplay_character__fandom') \
        .prefetch_related('reviews__customer') \
        .annotate(reviews_count=Count('reviews'),
                  average_score=Avg('reviews__score')).all()


class OrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = OrderSerializer
    queryset = Order.objects.prefetch_related(
        Prefetch('order_items__product', queryset=Product.objects.annotate(
            reviews_count=Count('reviews'),
            average_score=Avg('reviews__score')
        ).prefetch_related('seller', 'reviews'))).all()


class CreditCardDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CreditCardSerializer
    queryset = CreditCard.objects.select_related('user').all()


class ReviewDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ReviewSerializer
    queryset = Review.objects.select_related('product', 'customer').all()


# Cart Views
@api_view(['POST'])
def add_product_to_cart(request, product_id):
    try:
        product = Product.objects.select_related('seller', 'cosplay_character__fandom').annotate(
            reviews_count=Count('reviews'),
            average_score=Avg('reviews__score')).get(pk=product_id)
    except Product.DoesNotExist:
        return Response({'error': 'Товар не найден'}, status=status.HTTP_404_NOT_FOUND)
    
    cart = Cart(request)
    cart.add(product)

    return Response(status=status.HTTP_200_OK)
    

class ReduceProductQuantityInCartView(APIView):
    def post(self, request, product_id):
        try:
            product = Product.objects.select_related('seller', 'cosplay_character__fandom').annotate(
                reviews_count=Count('reviews'),
                average_score=Avg('reviews__score')).get(pk=product_id)
        except Product.DoesNotExist:
            return Response({'error': 'Товар не найден'}, status=status.HTTP_404_NOT_FOUND)
        
        cart = Cart(request)
        cart.add(product, quantity=-1)

        return Response(status=status.HTTP_200_OK)
    

class DeleteFromCartView(APIView):
    def delete(self, request, product_id):
        try:
            product = Product.objects.get(pk=product_id)
        except Product.DoesNotExist:
            return Response({'error': 'Товар не найден'}, status=status.HTTP_404_NOT_FOUND)
        
        cart = Cart(request)
        cart.remove(product)

        return Response(status=status.HTTP_200_OK)
    

class CartListView(APIView):
    def get(self, request):
        cart = Cart(request)
        cart_items = cart.get_cart_items()
        serializer = CartItemSerializer(cart_items, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)