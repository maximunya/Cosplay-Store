from django.db.models import Count, Avg, Prefetch, Q, Sum
from django.shortcuts import get_object_or_404

from rest_framework import generics
from rest_framework.permissions import IsAdminUser

from products.models import Product

from . import serializers
from .models import Fandom, Character
from .permissions import IsAdminOrReadOnly




class FandomCreateView(generics.CreateAPIView):
    serializer_class = serializers.FandomCreateSerializer
    permission_classes = (IsAdminUser,)


class FandomListView(generics.ListAPIView):
    serializer_class = serializers.FandomListSerializer
    queryset = Fandom.objects.annotate(
        characters_count=Count('characters'),
        total_fandom_products_count=Count(
            'characters__products', 
            filter=Q(characters__products__is_active=True))).all()


class FandomDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = serializers.FandomDetailSerializer
    permission_classes = (IsAdminOrReadOnly,)
    lookup_field = 'slug'

    def get_queryset(self):
        return Fandom.objects.annotate(
            characters_count=Count('characters'),
            total_fandom_products_count=Count('characters__products', distinct=True)
            ).prefetch_related(
                Prefetch('characters', queryset=Character.objects.annotate(
                    products_count=Count('products', filter=Q(products__is_active=True)
            )))).all()


class CharacterCreateView(generics.CreateAPIView):
    serializer_class = serializers.CharacterCreateSerializer
    permission_classes = (IsAdminUser,)

    def perform_create(self, serializer):
        fandom = get_object_or_404(Fandom, slug=self.kwargs['fandom_slug'])
        serializer.save(fandom=fandom)


class CharacterListView(generics.ListAPIView):
    serializer_class = serializers.CharacterListSerializer
    queryset = Character.objects.select_related('fandom').annotate(
        products_count=Count('products', filter=Q(products__is_active=True))).all()
    

class CharacterDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = serializers.CharacterDetailSerializer
    permission_classes = (IsAdminOrReadOnly,)
    lookup_field = 'slug'
    
    def get_queryset(self):
        fandom = get_object_or_404(Fandom, slug=self.kwargs['fandom_slug'])
        queryset = Character.objects.annotate(
            products_count=Count('products', filter=Q(products__is_active=True))
            ).select_related('fandom').prefetch_related(
            Prefetch('products', queryset=Product.objects.filter(is_active=True).annotate(
                reviews_count=Count('reviews'),
                average_score=Avg('reviews__score'),
                total_ordered_quantity=Sum('ordered_products__quantity')
            ).prefetch_related('product_images'
            ).select_related('seller', 'cosplay_character__fandom'))
            ).filter(fandom=fandom, slug=self.kwargs['slug'])
        return queryset

