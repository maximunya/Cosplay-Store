from django.db.models import Count, Avg, Prefetch, Q, Sum, FloatField, Case, When, F
from django.shortcuts import get_object_or_404
from django.db.models.functions import Coalesce

from rest_framework import generics, filters
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django_elasticsearch_dsl.search import Search

from products.models import Product

from . import serializers
from .models import Fandom, Character
from .permissions import IsAdminOrReadOnly


class FandomCreateView(generics.CreateAPIView):
    serializer_class = serializers.FandomCreateSerializer
    permission_classes = (IsAdminUser,)


class FandomListView(generics.ListAPIView):
    '''Returns a list of Fandoms'''
    serializer_class = serializers.FandomListSerializer
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter)
    filterset_fields = {'fandom_type': ['exact']}
    search_fields = ['name']
    ordering_fields = ['name', 'fandom_type',
                       'characters_count',
                       'total_fandom_products_count']
    ordering = ['-total_fandom_products_count', 'name']
    queryset = Fandom.objects.annotate(
        characters_count=Count('characters', distinct=True),
        total_fandom_products_count=Count(
            'characters__products', 
            filter=Q(characters__products__is_active=True),
            distinct=True))


class FandomDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = serializers.FandomDetailSerializer
    permission_classes = (IsAdminOrReadOnly,)
    lookup_field = 'slug'
    filter_fields = ['products_count__gt']
    ordering_fields = ['products_count', 'name', '-products_count', '-name']
    search_fields = ['name']

    def get_queryset(self):
        search_query = self.request.query_params.get('q', '')
        filters = {k: v for k, v in self.request.query_params.items() if k in self.filter_fields}
        order_by = self.request.query_params.get('ordering', 'name')
        ordering = order_by if order_by in self.ordering_fields else 'name'
        
        if search_query:
            filters['name__icontains'] = search_query

        return Fandom.objects.annotate(
            characters_count=Count('characters', distinct=True),
            total_fandom_products_count=Count('characters__products', 
                filter=Q(characters__products__is_active=True), distinct=True)
            ).prefetch_related(
                Prefetch('characters', queryset=Character.objects.annotate(
                    products_count=Count('products', filter=Q(products__is_active=True), distinct=True)
                    ).filter(**filters).order_by(ordering)
            )).all()
    
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        characters = self.object.characters.all()

        page = self.paginate_queryset(characters)
        if page is not None:
            serializer = serializers.FandomDetailSerializer(self.object)
            data = serializer.data
            data['characters'] = serializers.CharacterProductsCountSerializer(page, many=True).data
            return self.get_paginated_response(data)

        serializer = serializers.FandomDetailSerializer(self.object, context={'request': request})
        return Response(serializer.data)


class CharacterCreateView(generics.CreateAPIView):
    serializer_class = serializers.CharacterCreateSerializer
    permission_classes = (IsAdminUser,)

    def perform_create(self, serializer):
        fandom = get_object_or_404(Fandom, slug=self.kwargs['fandom_slug'])
        serializer.save(fandom=fandom)


class CharacterListView(generics.ListAPIView):
    serializer_class = serializers.CharacterListSerializer
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter)
    filterset_fields = {'fandom__fandom_type': ['exact']}
    search_fields = ['name']
    ordering_fields = ['name', 'fandom__name', 'fandom__fandom_type', 'products_count']
    ordering = ['-products_count', 'name']
    queryset = Character.objects.select_related('fandom').annotate(
        products_count=Count('products', filter=Q(products__is_active=True))).all()
    

class CharacterDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = serializers.CharacterDetailSerializer
    permission_classes = (IsAdminOrReadOnly,)
    lookup_field = 'slug'
    ordering_fields = [
        'timestamp', 'average_score', 'total_ordered_quantity',
        'reviews_count', 'actual_price', 'discount', 'title', 'in_stock',
        '-timestamp', '-average_score', '-total_ordered_quantity',
        '-reviews_count', '-actual_price', '-discount', '-title', '-in_stock'
    ]
    filter_fields = [
        'average_score__gt', 'actual_price__gt', 'actual_price__lt',
        'discount__gt', 'product_type', 'total_ordered_quantity__gt',
        'size', 'shoes_size', 'seller__name', 'seller__organization_name'
    ]
    search_fields = [
        'title', 'description', 'size', 'shoes_size',
        'product_type', 'seller.name', 'seller.organization_name'
    ]
    
    def get_queryset(self):
        fandom = get_object_or_404(Fandom, slug=self.kwargs['fandom_slug'])

        search_query = self.request.query_params.get('q', '')
        filters = {k: v for k, v in self.request.query_params.items() if k in self.filter_fields}
        order_by = self.request.query_params.get('ordering', '-total_ordered_quantity')
        ordering = order_by if order_by in self.ordering_fields else '-total_ordered_quantity'

        search = Search(index='products')

        if search_query:
            search = search.query("multi_match",
                                  query=search_query,
                                  fields=self.search_fields,
                                  fuzziness="auto")
        
        results = search.execute()
        product_ids = [hit.id for hit in results]

        filters['pk__in'] = product_ids

        return Character.objects.annotate(
            products_count=Count('products', filter=Q(products__is_active=True))
            ).select_related('fandom').prefetch_related(
            Prefetch('products', queryset=Product.objects.annotate(
                reviews_count=Count('reviews', distinct=True),
                average_score=Coalesce(Avg('reviews__score'), 0, output_field=FloatField()),
                total_ordered_quantity=Coalesce(Sum('ordered_products__quantity'), 0),
                actual_price=Case( 
                    When(discount__gt=0, then=F('price') - (F('price') * F('discount') / 100)),
                    default=F('price'),
                    output_field=FloatField()
                )   
                ).prefetch_related('product_images'
                ).select_related('seller', 'cosplay_character__fandom'
                ).filter(is_active=True, **filters).order_by(ordering, '-timestamp'))
            ).filter(fandom=fandom)
    
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        products = self.object.products.all()

        page = self.paginate_queryset(products)
        if page is not None:
            serializer = serializers.CharacterDetailSerializer(self.object)
            data = serializer.data
            data['products'] = serializers.ProductSerializer(page, many=True).data
            return self.get_paginated_response(data)

        serializer = serializers.CharacterDetailSerializer(self.object, context={'request': request})
        return Response(serializer.data)

