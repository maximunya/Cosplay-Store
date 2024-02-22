from django.db.models import Count, Avg, Sum
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from rest_framework import generics

from common.serializers import (
    ProductSerializer,
    ProductDetailSerializer,
    ReviewSerializer,
    AnswerSerializer
)

from .models import Product, Review, Answer
from .serializers import ReviewCreateSerializer
from . import permissions


User = get_user_model()


class ProductListView(generics.ListAPIView):
    serializer_class = ProductSerializer
    queryset = Product.objects.select_related(
        'seller', 'cosplay_character__fandom').annotate(
            reviews_count=Count('reviews'),
            average_score=Avg('reviews__score'),
            total_ordered_quantity=Sum('ordered_products__quantity')
        ).prefetch_related('reviews', 'product_images').filter(is_active=True)
    

class ProductDetailView(generics.RetrieveAPIView):
    serializer_class = ProductDetailSerializer
    queryset = Product.objects.select_related(
            'seller', 'cosplay_character__fandom',
        ).prefetch_related(
            'reviews__customer', 'reviews__answers__seller',
            'product_images', 'seller__employees') \
        .annotate(
            reviews_count=Count('reviews'),
            average_score=Avg('reviews__score'),
            total_ordered_quantity=Sum('ordered_products__quantity')
        ).filter(is_active=True)
    lookup_field = 'slug'
    
    
class ReviewCreateView(generics.CreateAPIView):
    serializer_class = ReviewCreateSerializer
    permission_classes = (permissions.IsCustomerOrAdminUser,)

    def perform_create(self, serializer):
        user = self.request.user
        product = get_object_or_404(Product, pk=self.kwargs['pk'], is_active=True)
        serializer.save(customer=user, product=product)


class ReviewDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ReviewSerializer
    permission_classes = (permissions.IsAuthorOrAdminOrReadOnly,)
   
    def get_queryset(self):
        product = get_object_or_404(Product, pk=self.kwargs['product_id'])

        return Review.objects.select_related('product', 'customer'
            ).prefetch_related('answers__seller'
            ).filter(product=product)
    

class AnswerDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AnswerSerializer
    permission_classes = (permissions.IsSellerOrReadOnly,)

    def get_queryset(self):
        product = get_object_or_404(Product, pk=self.kwargs['product_id'])

        return Answer.objects.select_related('seller', 'review__product'
            ).prefetch_related('seller__employees'
            ).filter(review__product=product)



