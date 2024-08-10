from rest_framework.test import APITestCase
from rest_framework import status
from django.db.models import Count, Avg, Sum, F, Case, When, FloatField
from django.db.models.functions import Coalesce
from django.urls import reverse

from .models import Product
from common.serializers import ProductSerializer


class ProductTests(APITestCase):
    def test_get_serialized_products(self):
        url = reverse('products:product-list')
        response = self.client.get(url)

        queryset = Product.objects.select_related(
            'seller', 'cosplay_character__fandom').annotate(
            reviews_count=Count('reviews', distinct=True),
            average_score=Coalesce(Avg('reviews__score'), 0, output_field=FloatField()),
            total_ordered_quantity=Coalesce(Sum('ordered_products__quantity'), 0),
            actual_price=Case(
                When(discount__gt=0, then=F('price') - (F('price') * F('discount') / 100)),
                default=F('price'),
                output_field=FloatField()
            )
        ).prefetch_related('reviews', 'product_images').all()
        serializer_data = ProductSerializer(queryset, many=True).data

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer_data)
