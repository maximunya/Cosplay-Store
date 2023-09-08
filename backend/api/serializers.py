from rest_framework import serializers
from .models import (Fandom, Character, Product, Review, CreditCard, 
		             Order, Favorite, OrderItem, ProductImage)

from djoser.serializers import UserCreateSerializer, UserSerializer

from django.contrib.auth import get_user_model
User = get_user_model()


# Default Serializers
class SimpleUserSerializer(UserSerializer):
	class Meta(UserSerializer.Meta):
		model = User
		fields = ('id', 'username', 'profile_pic', 'phone_number')
		

class CreditCardSerializer(serializers.ModelSerializer):
	class Meta:
		model = CreditCard
		fields = ('id', 'card_number', 'user')


class FandomSerializer(serializers.ModelSerializer):
	characters_count = serializers.IntegerField(read_only=True)
	products_count = serializers.SerializerMethodField()

	def get_products_count(self, fandom):
		products = []
		for character in fandom.characters.all():
			products.extend(character.products.all())
		return len(products)

	class Meta:
		model = Fandom
		fields = ('id', 'fandom_type', 'name', 'characters_count', 'products_count')


class SimpleFandomSerializer(serializers.ModelSerializer):
	class Meta:
		model = Fandom
		fields = ('id', 'fandom_type', 'name',)


class CharacterSerializer(serializers.ModelSerializer):
	class Meta:
		model = Character
		fields = ('id', 'name',)


class ExtendedCharacterSerializer(serializers.ModelSerializer):
	products_count = serializers.IntegerField(read_only=True)

	class Meta:
		model = Character
		fields = ('id', 'name', 'products_count',)


class CharacterFandomSerializer(serializers.ModelSerializer):
	fandom = SimpleFandomSerializer(read_only=True)

	class Meta:
		model = Character
		fields = ('id', 'fandom', 'name',)


class ProductSerializer(serializers.ModelSerializer):
	seller = SimpleUserSerializer(read_only=True)
	cosplay_character = CharacterFandomSerializer(read_only=True)
	reviews_count = serializers.IntegerField(read_only=True)
	average_score = serializers.SerializerMethodField()

	def get_average_score(self, product):
		if product.average_score:
			average_score = round(product.average_score, 1)
			return average_score
		return product.average_score

	class Meta:
		model = Product
		fields = ('id', 'title', 'cosplay_character', 'seller',
	              'price', 'product_type', 'timestamp',
				  'reviews_count', 'average_score', 'is_active',)


class ReviewSerializer(serializers.ModelSerializer):
	customer = SimpleUserSerializer(read_only=True)
	product = serializers.SlugRelatedField(slug_field='id', read_only=True)

	class Meta:
		model = Review
		fields = ('id', 'product', 'customer', 'text', 
				  'score', 'timestamp', 'edited',)		


class SimpleProductSerializer(serializers.ModelSerializer):
	seller = SimpleUserSerializer(read_only=True)
	cosplay_character = CharacterSerializer(read_only=True)
	reviews_count = serializers.IntegerField(read_only=True)
	average_score = serializers.SerializerMethodField()

	def get_average_score(self, product):
		if product.average_score:
			average_score = round(product.average_score, 1)
			return average_score
		return product.average_score

	class Meta:
		model = Product
		fields = ('id', 'title', 'seller', 'cosplay_character', 'is_active',
	              'price', 'product_type', 'timestamp', 'reviews_count', 'average_score')
		

class CartItemSerializer(serializers.Serializer):
	product = SimpleProductSerializer()
	quantity = serializers.IntegerField()
	price = serializers.IntegerField()
	total_price = serializers.IntegerField()


class CartSerializer(serializers.Serializer):
	cart_length = serializers.IntegerField()
	cart_items = serializers.ListField()
	total_cart_price = serializers.IntegerField()


class OrderItemSerializer(serializers.ModelSerializer):
	product = SimpleProductSerializer(read_only=True)
	price = serializers.SerializerMethodField()
	
	def get_price(self, order_item):
		price = order_item.get_price()
		return price

	class Meta:
		model = OrderItem
		fields = ('id', 'product', 'order', 'quantity', 'price')


class OrderSerializer(serializers.ModelSerializer):
	order_items = OrderItemSerializer(many=True, read_only=True)
	customer = SimpleUserSerializer(read_only=True)
	total_price = serializers.SerializerMethodField()


	def get_total_price(self, order):
		return order.get_order_price()

	class Meta:
		model = Order
		fields = ('id', 'customer', 'name', 'email', 'phone_number', 'order_items', 'address', 'status', 'timestamp', 'total_price')

	
class FavoriteSerializer(serializers.ModelSerializer):
	class Meta:
		model = CreditCard
		fields = '__all__'
		

# Create Serializers
class CreateFandomSerializer(serializers.ModelSerializer):
	class Meta:
		model = Fandom
		fields = '__all__'


class CreateCharacterSerializer(serializers.ModelSerializer):
	class Meta:
		model = Character
		fields = '__all__'


class CreateProductSerializer(serializers.ModelSerializer):
	class Meta:
		model = Product
		fields = '__all__'


class CreateOrderAuthenticatedSerializer(serializers.ModelSerializer):
	order_items = OrderItemSerializer(many=True, read_only=True)
	customer = SimpleUserSerializer(read_only=True)

	class Meta:
		model = Order
		fields = ('id', 'customer', 'address', 'order_items', 'timestamp')


class CreateOrderSerializer(serializers.ModelSerializer):
	order_items = OrderItemSerializer(many=True, read_only=True)

	class Meta:
		model = Order
		fields = ('id', 'name', 'email', 'phone_number', 'order_items', 'address', 'timestamp')


class CreateReviewSerializer(serializers.ModelSerializer):
	class Meta:
		model = Review
		fields = '__all__'


class CreateCreditCardSerializer(serializers.ModelSerializer):
	class Meta:
		model = CreditCard
		fields = fields = '__all__'


class UserCreateSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = ['id', 'username', 'email', 'password']


# Detail Serializers
class UserDetailSerializer(serializers.ModelSerializer):
	credit_cards = CreditCardSerializer(read_only=True, many=True)

	class Meta:
		model = User
		fields = (
			'id', 'username', 'email', 'first_name',
	    	'last_name', 'phone_number', 'is_active',
			'is_superuser', 'is_staff', 'last_login',
			'date_joined', 'profile_pic', 'credit_cards',
			)


class CharacterDetailSerializer(serializers.ModelSerializer):
	fandom = SimpleFandomSerializer(read_only=True)
	products_count = serializers.IntegerField(read_only=True)

	class Meta:
		model = Character
		fields = ('id', 'name', 'products_count', 'fandom',)


class ProductDetailSerializer(ProductSerializer):
	reviews = ReviewSerializer(many=True, read_only=True)
	
	class Meta(ProductSerializer.Meta):
		model = Product
		fields = ('id', 'title', 'cosplay_character', 'seller',
	              'price', 'product_type', 'description', 
				  'size', 'shoes_size', 'timestamp', 'reviews_count',
				  'average_score', 'is_active', 'reviews',)


class OrderDetailSerializer(serializers.ModelSerializer):
	order_items = OrderItemSerializer(many=True, read_only=True)

	class Meta:
		model = Order
		fields = ('order_items',)


# Other serializers
class CustomUserSerializer(UserSerializer):
	class Meta(UserSerializer.Meta):
		model = User
		fields = (
			'id', 'username', 'email', 'first_name',
	    	'last_name', 'phone_number', 'is_active',
			'is_superuser', 'is_staff', 'last_login',
			'date_joined', 'profile_pic', 'groups', 
			'user_permissions',
			)


class SimpleProductSerializer(serializers.ModelSerializer):
	seller = SimpleUserSerializer(read_only=True)
	cosplay_character = CharacterSerializer(read_only=True)
	reviews_count = serializers.IntegerField(read_only=True)
	average_score = serializers.SerializerMethodField()

	def get_average_score(self, product):
		if product.average_score:
			average_score = round(product.average_score, 1)
			return average_score
		return product.average_score

	class Meta:
		model = Product
		fields = ('id', 'title', 'seller', 'cosplay_character', 'is_active',
	              'price', 'product_type', 'timestamp', 'reviews_count', 'average_score')


class CharacterProductSerializer(serializers.ModelSerializer):
	products = SimpleProductSerializer(many=True, read_only=True)
	fandom = SimpleFandomSerializer(read_only=True)
	products_count = serializers.IntegerField(read_only=True)

	class Meta:
		model = Character
		fields = ('id', 'name', 'fandom', 'products_count', 'products',)


class FandomCharacterSerializer(serializers.ModelSerializer):
	characters = ExtendedCharacterSerializer(many=True, read_only=True)
	characters_count = serializers.IntegerField(read_only=True)

	class Meta:
		model = Fandom
		fields = ('id', 'fandom_type', 'name', 'characters_count', 'characters',)


class FandomProductSerializer(serializers.ModelSerializer):
	products = serializers.SerializerMethodField()
	characters = ExtendedCharacterSerializer(read_only=True, many=True)
	characters_count = serializers.IntegerField(read_only=True)
	products_count = serializers.SerializerMethodField()

	def get_products(self, fandom):
		characters = fandom.characters.all()
		products = []
		for character in characters:
			character_products = character.products.all()
			products.extend(character_products)
		return SimpleProductSerializer(products, many=True).data
	
	def get_products_count(self, fandom):
		products = []
		for character in fandom.characters.all():
			products.extend(character.products.all())
		return len(products)

	class Meta:
		model = Fandom
		fields = ('id', 'fandom_type', 'name', 'characters_count', 'characters', 'products_count', 'products',)
