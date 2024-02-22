from rest_framework import serializers

from common.serializers import ProductSerializer

from .models import CartItem


class CartItemSerializer(serializers.Serializer):
	product = ProductSerializer(many=False, read_only=True)
	quantity = serializers.IntegerField()
	price = serializers.IntegerField()
	total_price = serializers.IntegerField()


class CartItemAuthenticatedSerializer(serializers.Serializer):
	product = ProductSerializer(many=False, read_only=True)
	quantity = serializers.IntegerField()
	price = serializers.SerializerMethodField()
	total_price = serializers.SerializerMethodField()

	def get_price(self, cart_item):
		return cart_item.product.get_real_price()

	def get_total_price(self, cart_item):
		return cart_item.get_total_price()
	
	class Meta:
		model = CartItem
		fields = ('id', 'product', 'quantity', 'price', 'total_price')


class CartSerializer(serializers.Serializer):
	cart_length = serializers.IntegerField()
	cart_items = serializers.ListField()
	total_cart_price = serializers.IntegerField()