from django.shortcuts import get_object_or_404
from django.db.models import Count, Avg, Prefetch, Sum

from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view

from products.models import Product

from .models import CartItem
from .cart import Cart
from .serializers import (
    CartItemAuthenticatedSerializer, 
    CartItemSerializer, 
    CartSerializer
)


@api_view(['POST'])
def add_product_to_cart(request, product_id, quantity=1):
    user = request.user
    product = get_object_or_404(Product, pk=product_id, is_active=True)

    if product.in_stock and product.in_stock < quantity:
        return Response({'error': 'Insufficient product quantity in stock.'}, status=status.HTTP_400_BAD_REQUEST)
    
    else:
        if user.is_authenticated:
            cart_item, created = CartItem.objects.get_or_create(user=user, product=product)
            if created:
                cart_item.quantity = quantity
            else:
                cart_item.quantity += quantity
            cart_item.save()
        else:
            cart = Cart(request)
            cart_item = cart.add(product, quantity)
        return Response({'message': 'Product was successfully added to your cart.'}, status=status.HTTP_201_CREATED)


@api_view(['POST'])
def reduce_product_quantity_in_cart(request, product_id, quantity=1):
    user = request.user
    product = get_object_or_404(Product, pk=product_id)

    if user.is_authenticated:
        try:
            cart_item = CartItem.objects.get(user=user, product=product)
            if cart_item.quantity == quantity:
                cart_item.delete()
                return Response({'message': 'Product was deleted from your cart.'}, status=status.HTTP_200_OK)
            else:
                cart_item.quantity -= quantity
                cart_item.save()
                return Response({'message': 'Product quantity in your cart was reduced.'}, status=status.HTTP_200_OK)
        except CartItem.DoesNotExist:
            return Response({'error': 'Cart item does not exist.'}, status=status.HTTP_404_NOT_FOUND)
    else:
        cart = Cart(request)
        response_message = cart.reduce(product, quantity)
        return Response(response_message, status=status.HTTP_200_OK)
    

@api_view(['DELETE'])
def delete_from_cart(request, product_id):
    user = request.user
    product = get_object_or_404(Product, pk=product_id)

    if user.is_authenticated:
        try:
            cart_item = CartItem.objects.get(user=user, product=product)
            cart_item.delete()
            return Response({'message': 'Product was deleted from your cart.'}, status=status.HTTP_200_OK)
        except CartItem.DoesNotExist:
            return Response({'error': 'Cart item does not exist.'}, status=status.HTTP_404_NOT_FOUND)
    else:
        cart = Cart(request)
        response_message = cart.remove(product)
        return Response(response_message, status=status.HTTP_200_OK)


@api_view(['GET'])
def cart_list(request):
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

        cart_length = sum(item.quantity for item in cart_items)
        total_cart_price = sum(item.get_total_price() for item in cart_items)

        data = {
            'cart_length': cart_length,
            'cart_items': CartItemAuthenticatedSerializer(cart_items, many=True).data,
            'total_cart_price': total_cart_price
        }
    else:
        cart = Cart(request)
        cart_items = cart.get_cart_items()
        cart_length = cart.__len__()
        total_cart_price = cart.get_total_cart_price()

        data = {
            'cart_length': cart_length,
            'cart_items': CartItemSerializer(cart_items, many=True).data,
            'total_cart_price': total_cart_price
        }
        
    serializer = CartSerializer(data)
    return Response(serializer.data, status=status.HTTP_200_OK)
