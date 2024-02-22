from django.shortcuts import get_object_or_404
from django.db.models import Count, Avg, Sum, Prefetch

from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from products.models import Product

from .serializers import FavoriteListSerializer
from .models import Favorite


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def manage_favorite_item(request, product_id):
    user = request.user
    product = get_object_or_404(Product, pk=product_id, is_active=True)

    favorite_item, created = Favorite.objects.get_or_create(user=user, product=product)
    if created:
        message = 'Product was added to your favorites.'
    else:
        favorite_item.delete()
        message = 'Product was removed from your favorites.'
    return Response({'message': message}, status=status.HTTP_200_OK)
    

class FavoriteListView(generics.ListAPIView):
    serializer_class = FavoriteListSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        return Favorite.objects.filter(user=user).prefetch_related(
            Prefetch('product', queryset=Product.objects.annotate(
                reviews_count=Count('reviews'),
                average_score=Avg('reviews__score'),
                total_ordered_quantity=Sum('ordered_products__quantity')
            ).prefetch_related('reviews', 'product_images'
            ).select_related('seller', 'cosplay_character__fandom'
            ).filter(is_active=True)))
