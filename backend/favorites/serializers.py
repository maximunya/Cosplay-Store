from rest_framework import serializers
from .models import Favorite

from common_serializers import ProductSerializer


class FavoriteListSerializer(serializers.ModelSerializer):
	product = ProductSerializer(read_only=True)

	class Meta:
		model = Favorite
		fields = '__all__'