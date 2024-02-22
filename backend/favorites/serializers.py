from rest_framework import serializers

from common.serializers import ProductSerializer

from .models import Favorite


class FavoriteListSerializer(serializers.ModelSerializer):
	product = ProductSerializer(read_only=True)

	class Meta:
		model = Favorite
		fields = '__all__'