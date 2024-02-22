from rest_framework import serializers
from .models import Order, OrderItem

from users.models import Address
from users.serializers import AddressSerializer
from cards.models import Card
from cards.serializers import CardSimpleSerializer
	
from common_serializers import (
	UserSimpleSerializer,
	AddressSimpleSerializer,
	CardListSerializer,
	ProductSerializer,
)


class OrderItemSerializer(serializers.ModelSerializer):
	product = ProductSerializer(read_only=True)
	total_price = serializers.SerializerMethodField()
	order = serializers.SlugRelatedField(read_only=True, slug_field='slug')
	
	def get_total_price(self, order_item):
		total_price = order_item.get_total_price()
		return total_price

	class Meta:
		model = OrderItem
		fields = ('id', 'slug', 'product', 'order', 'quantity', 'price', 'total_price')


class OrderCartSerializer(serializers.Serializer):
	cart_length = serializers.IntegerField()
	cart_items = serializers.ListField()
	total_cart_price = serializers.IntegerField()
	name = serializers.CharField()
	email = serializers.EmailField()
	phone_number = serializers.CharField()
	addresses = AddressSimpleSerializer(many=True)
	cards = CardListSerializer(many=True)
	

class OrderListSerializer(serializers.ModelSerializer):
	order_images = serializers.SerializerMethodField()
	
	def get_order_images(self, order):
		order_images = []
		for item in order.order_items.all():
			item_product_images = item.product.product_images.all()
			if item_product_images:
				order_images.append(item_product_images[0].image.url)
		return order_images

	class Meta:
		model = Order
		fields = ('id', 'slug', 'order_images', 'status',
			      'created_at', 'updated_at', 'total_order_price')


class OrderCreateAuthenticatedSerializer(serializers.ModelSerializer):
	order_items = OrderItemSerializer(many=True, read_only=True)
	customer = UserSimpleSerializer(read_only=True)
	name = serializers.CharField(required=False)
	email = serializers.EmailField(read_only=True)
	phone_number = serializers.CharField(required=False)
	address = serializers.PrimaryKeyRelatedField(queryset=Address.objects.all())
	card = serializers.PrimaryKeyRelatedField(queryset=Card.objects.all())
	total_order_price = serializers.IntegerField(read_only=True)

	class Meta:
		model = Order
		fields = ('customer', 'name', 'email', 'phone_number', 'order_items',
				  'address', 'card', 'created_at', 'updated_at', 'total_order_price')

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		user = self.context['request'].user

		self.fields['address'].queryset = user.addresses.all()
		self.fields['card'].queryset = user.cards.all()

		if not user.first_name:
			self.fields['name'] = serializers.CharField(required=True)

		if not user.phone_number:
			self.fields['phone_number'] = serializers.CharField(required=True, max_length=12, min_length=11)

		if not user.addresses.all():
			self.fields['address'] = serializers.CharField(required=True)

		if not user.cards.all():
			self.fields['card'] = serializers.CharField(max_length=16, min_length=16, required=True)

	def validate_address(self, value):
		user = self.context['request'].user
		if value and user.addresses.all() and value not in user.addresses.all():
			raise serializers.ValidationError("This is not your address.")
		return value
	
	def validate_card(self, value):
		user = self.context['request'].user
		if not user.cards.all():
			if not value.isdigit():
				raise serializers.ValidationError("Incorrect card number format.")
		else:
			if value and value not in user.cards.all():
				raise serializers.ValidationError("This is not your card.")
		return value
	
	def validate_phone_number(self, value):
		if len(value) == 11 and value.isdigit():
			return value
		elif len(value) == 12 and value.startswith('+') and value[1:].isdigit():
			return value
		else:
			raise serializers.ValidationError("Incorrect phone number format.")
		
	def validate_name(self, value):
		if not value.isalpha():
			raise serializers.ValidationError("Incorrect name format.")
		return value


class OrderCreateSerializer(serializers.ModelSerializer):
	card = serializers.CharField(max_length=16, min_length=16)
	address = serializers.CharField()
	order_items = OrderItemSerializer(many=True, read_only=True)
	total_order_price = serializers.IntegerField(read_only=True)

	class Meta:
		model = Order
		fields = ('customer', 'name', 'email', 'phone_number', 'order_items',
				  'address', 'card', 'created_at', 'updated_at', 'total_order_price')

	def validate_card(self, value):
		if not value.isdigit():
			raise serializers.ValidationError("Incorrect card number format.")
		return value
	
	def validate_name(self, value):
		if not value.isalpha():
			raise serializers.ValidationError("Incorrect name format.")
		return value
	
	def validate_phone_number(self, value):
		if len(value) == 11 and value.isdigit():
			return value
		if len(value) == 12 and value.startswith('+') and value[-11:].isdigit():
			return value
		else:
			raise serializers.ValidationError("Incorrect phone number format.")
		

class OrderDetailSerializer(serializers.ModelSerializer):
	customer = UserSimpleSerializer()
	order_items = OrderItemSerializer(many=True, read_only=True)
	ordered_products_amount = serializers.IntegerField()
	total_order_items_quantity = serializers.IntegerField()
	card = CardListSerializer(read_only=True)
	address = AddressSerializer(read_only=True)

	class Meta:
		model = Order
		fields = ('id', 'slug', 'customer', 'name', 
			      'email', 'phone_number', 'ordered_products_amount',
				  'total_order_items_quantity',
			      'order_items', 'address', 'card',
				  'status', 'created_at', 'updated_at', 'total_order_price')
		

class OrderSimpleSerializer(serializers.ModelSerializer):
	customer = UserSimpleSerializer()
	address = serializers.SlugRelatedField(slug_field='address', read_only=True)

	class Meta:
		model = Order
		fields = ('slug', 'customer', 'name', 'email',
			      'phone_number', 'address',)