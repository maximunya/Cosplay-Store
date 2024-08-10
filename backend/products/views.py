from django.db.models import Count, Avg, Sum, F, Case, When, FloatField
from django.db.models.functions import Coalesce
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from rest_framework import generics

from common.serializers import (
    ProductSerializer,
    ProductDetailSerializer,
    ReviewSerializer,
    AnswerSerializer
)

from .documents import ProductDocument
from .models import Product, Review, Answer
from .serializers import ReviewCreateSerializer
from . import permissions

User = get_user_model()


class ProductListView(generics.ListAPIView):
    serializer_class = ProductSerializer
    ordering_fields = [
        'timestamp', 'average_score', 'total_ordered_quantity',
        'reviews_count', 'actual_price', 'discount', 'title', 'in_stock',
        '-timestamp', '-average_score', '-total_ordered_quantity',
        '-reviews_count', '-actual_price', '-discount', '-title', '-in_stock'
    ]
    filter_fields = [
        'id', 'price__gte', 'price__lte', 'discount__gte', 'average_score__gte',
        'cosplay_character__name__exact', 'cosplay_character__fandom__name__exact',
        'cosplay_character__fandom__fandom_type', 'product_type__exact', 'size__exact',
        'shoes_size__exact', 'seller__name__exact', 'seller__organization_name__exact',
        'seller__is_admin_store', 'seller__is_verified',
        'total_ordered_quantity__gte', 'total_ordered_quantity__lte'
    ]
    search_fields = [
        'title', 'description', 'size', 'shoes_size',
        'cosplay_character.name', 'cosplay_character.fandom.name',
        'cosplay_character.fandom.fandom_type', 'product_type',
        'seller.name', 'seller.organization_name'
    ]

    def get_queryset(self):
        search_query = self.request.query_params.get('q', '')
        order_by = self.request.query_params.get('ordering', '-total_ordered_quantity')
        ordering = order_by if order_by in self.ordering_fields else '-total_ordered_quantity'
        filters = {k: v for k, v in self.request.query_params.items() if k in self.filter_fields}

        search = ProductDocument.search().extra(size=1000)

        # Filtering
        for field, value in filters.items():
            if field in ['price__gte', 'price__lte',
                         'discount__lte', 'discount__gte',
                         'average_score__gte', 'average_score__lte']:
                field_name, operator = field.rsplit('__', 1)
                search = search.filter('range', **{field_name: {operator: value}})
            else:
                search = search.filter('term', **{field: value})

        # Searching
        if search_query:
            search = search.query("multi_match",
                                  query=search_query,
                                  fields=self.search_fields,
                                  fuzziness="auto")

        results = search.execute()
        product_ids = [hit.id for hit in results]

        return Product.objects.select_related(
            'seller', 'cosplay_character__fandom').annotate(
            reviews_count=Count('reviews', distinct=True),
            average_score=Coalesce(Avg('reviews__score'), 0, output_field=FloatField()),
            total_ordered_quantity=Coalesce(Sum('ordered_products__quantity'), 0),
            actual_price=Case(
                When(discount__gt=0, then=F('price') - (F('price') * F('discount') / 100)),
                default=F('price'),
                output_field=FloatField()
            )
        ).prefetch_related('reviews', 'product_images'
                           ).filter(is_active=True, pk__in=product_ids).order_by(ordering, '-timestamp')


class ProductDetailView(generics.RetrieveAPIView):
    serializer_class = ProductDetailSerializer
    queryset = Product.objects.select_related(
        'seller', 'cosplay_character__fandom',
    ).prefetch_related(
        'reviews__customer', 'reviews__answers__seller',
        'product_images', 'seller__employees') \
        .annotate(
        reviews_count=Count('reviews', distinct=True),
        average_score=Coalesce(Avg('reviews__score'), 0, output_field=FloatField()),
        total_ordered_quantity=Coalesce(Sum('ordered_products__quantity'), 0)
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
