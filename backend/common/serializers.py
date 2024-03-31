from django.apps import apps
from django.contrib.auth import get_user_model

from rest_framework import serializers
from djoser.serializers import UserSerializer


User = get_user_model()
Address = apps.get_model('users', 'Address')
Store = apps.get_model('stores', 'Store')
Fandom = apps.get_model('fandoms', 'Fandom')
Character = apps.get_model('fandoms', 'Character')
Card = apps.get_model('cards', 'Card')
Product = apps.get_model('products', 'Product')
ProductImage = apps.get_model('products', 'ProductImage')
Review = apps.get_model('products', 'Review')
Answer = apps.get_model('products', 'Answer')
OrderItem = apps.get_model('orders', 'OrderItem')


class UserSimpleSerializer(UserSerializer):
	class Meta(UserSerializer.Meta):
		model = User
		fields = ('id', 'username', 'is_staff', 'profile_pic',)
		

class StoreSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = ('id', 'slug', 'name', 'logo', 'is_verified', 'is_admin_store',)
		

class StoreListSerializer(serializers.ModelSerializer):
    products_count = serializers.IntegerField()
    store_average_score = serializers.SerializerMethodField()

    def get_store_average_score(self, store):
        if store.store_average_score:
            store_average_score = round(store.store_average_score, 1)
            return store_average_score
        return None

    class Meta:
        model = Store
        fields = ('id', 'slug', 'name', 'logo', 
                  'organization_type', 'organization_name',
                  'is_verified', 'is_admin_store',
                  'products_count', 'store_average_score')


class FandomSerializer(serializers.ModelSerializer):
	class Meta:
		model = Fandom
		fields = ('id', 'slug', 'name', 'fandom_type', 'image')


class CharacterSerializer(serializers.ModelSerializer):
	fandom = FandomSerializer(read_only=True)

	class Meta:
		model = Character
		fields = ('id', 'slug', 'name', 'fandom', 'image')
		

class CardListSerializer(serializers.ModelSerializer):
	class Meta:
		model = Card
		fields = ('id', 'uuid', 'name', 'card_number', 'balance', 'created_at')


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ('id', 'image')
		

class ProductSimpleSerializer(serializers.ModelSerializer):
	product_images = ProductImageSerializer(many=True, read_only=True)
	cosplay_character = CharacterSerializer(read_only=True)
	seller = StoreSimpleSerializer(read_only=True)

	class Meta:
		model = Product
		fields = ('id', 'slug', 'title', 'product_images', 'cosplay_character', 'seller')
		

class ProductSerializer(serializers.ModelSerializer):
	seller = StoreSimpleSerializer(read_only=True, many=False)
	product_images = ProductImageSerializer(many=True, read_only=True)
	real_price = serializers.SerializerMethodField()
	cosplay_character = CharacterSerializer(read_only=True)
	reviews_count = serializers.IntegerField(read_only=True)
	average_score = serializers.SerializerMethodField()
	total_ordered_quantity = serializers.IntegerField(read_only=True)

	class Meta:
		model = Product
		fields = ('id', 'slug', 'title', 'product_images', 
				  'cosplay_character', 'seller', 'is_active',
	              'price', 'real_price', 'discount', 'in_stock',
				  'product_type', 'timestamp', 'total_ordered_quantity',
				  'size', 'shoes_size', 'reviews_count', 'average_score')

	def get_real_price(self, product):
		return product.get_real_price()

	def get_average_score(self, product):
		if product.average_score:
			average_score = round(product.average_score, 1)
			return average_score
		return None
		

class AddressSimpleSerializer(serializers.ModelSerializer):
	class Meta:
		model = Address
		fields = ('id', 'address')
		

class AnswerSerializer(serializers.ModelSerializer):
	class Meta:
		model = Answer
		fields = '__all__'
		read_only_fields = ('seller', 'review')


class ReviewSerializer(serializers.ModelSerializer):
	customer = UserSimpleSerializer(read_only=True)
	product = serializers.SlugRelatedField(slug_field='slug', read_only=True)
	answers = AnswerSerializer(many=True, read_only=True)

	class Meta:
		model = Review
		fields = ('id', 'product', 'customer', 'text', 
				  'score', 'timestamp', 'edited', 'answers')
		

class ProductDetailSerializer(ProductSerializer):
	seller = StoreSimpleSerializer(read_only=True)
	product_images = ProductImageSerializer(many=True, read_only=True)
	reviews = ReviewSerializer(many=True, read_only=True)
	real_price = serializers.SerializerMethodField()
	total_ordered_quantity = serializers.IntegerField(read_only=True)
	reviews_count = serializers.IntegerField(read_only=True)
	average_score = serializers.SerializerMethodField()

	def get_real_price(self, product):
		return product.get_real_price()

	def get_average_score(self, product):
		if product.average_score:
			average_score = round(product.average_score, 1)
			return average_score
		return None
	
	class Meta(ProductSerializer.Meta):
		model = Product
		fields = ('id', 'slug', 'title', 'product_images', 'cosplay_character', 'seller',
	              'price', 'real_price', 'discount', 'product_type', 'description', 
				  'size', 'shoes_size', 'timestamp', 'reviews_count', 'in_stock',
				  'average_score', 'total_ordered_quantity', 'is_active', 'reviews',)
		

class OrderItemSimpleSerializer(serializers.ModelSerializer):
	total_price = serializers.SerializerMethodField()
	
	def get_total_price(self, order_item):
		total_price = order_item.get_total_price()
		return total_price

	class Meta:
		model = OrderItem
		fields = ('id', 'slug', 'quantity', 'price', 
			      'total_price', 'created_at', 'updated_at', 'status')