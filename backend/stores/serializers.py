from django.apps import apps
from django.contrib.auth import get_user_model

from rest_framework import serializers

from common_serializers import (
    ProductSerializer,
    ProductSimpleSerializer,
    OrderItemSimpleSerializer, 
    ProductDetailSerializer,
    UserSimpleSerializer,
    ProductImageSerializer,
    StoreSimpleSerializer,
)

from .models import Store, Employee
from orders.serializers import OrderSimpleSerializer


Transaction = apps.get_model('cards', 'Transaction')
Product = apps.get_model('products', 'Product')
OrderItem = apps.get_model('orders', 'OrderItem')


class StoreCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = ('organization_type', 'organization_name', 
                  'name', 'logo', 'taxpayer_number', 'check_number')

    def validate_organization_name(self, value):
        if value.isdigit():
            raise serializers.ValidationError("Organization name cannot consist only of digits.")
        return value

    def validate_name(self, value):
        if value.isdigit():
            raise serializers.ValidationError("Store name cannot consist only of digits.")
        return value

    def validate_taxpayer_number(self, value):
        if len(value) != 10 or not value.isdigit():
            raise serializers.ValidationError("Invalid taxpayer number.")
        return value
        
    def validate_check_number(self, value):
        if len(value) != 20 or not value.isdigit():
            raise serializers.ValidationError("Invalid check number.")
        return value
        

class StoreDetailPrivateSerializer(serializers.ModelSerializer):
    owner = serializers.SlugRelatedField(slug_field='username', read_only=True)

    class Meta:
        model = Store
        fields = '__all__'
        read_only_fields = ('id', 'slug', 'owner', 'balance', 
                            'is_verified', 'is_admin_store',)
        
    def validate_organization_name(self, value):
        if value.isdigit():
            raise serializers.ValidationError("Organization name cannot consist only of digits.")
        return value

    def validate_name(self, value):
        if value.isdigit():
            raise serializers.ValidationError("Store name cannot consist only of digits.")
        return value

    def validate_taxpayer_number(self, value):
        if len(value) != 10 or not value.isdigit():
            raise serializers.ValidationError("Invalid taxpayer number.")
        return value
        
    def validate_check_number(self, value):
        if len(value) != 20 or not value.isdigit():
            raise serializers.ValidationError("Invalid check number.")
        return value
        

class StoreDetailPublicSerializer(serializers.ModelSerializer):
    store_products = ProductSerializer(many=True)
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
                  'bio', 'created_at', 'products_count', 
                  'store_average_score', 'store_products')
        

class EmployeeCreateSerializer(serializers.ModelSerializer):
    username = serializers.CharField(write_only=True)
    user = UserSimpleSerializer(read_only=True)

    class Meta:
        model = Employee
        fields = ('user', 'username', 'is_admin')

    def validate_username(self, value):
        user_model = get_user_model()
        try:
            user = user_model.objects.get(username=value)
        except user_model.DoesNotExist:
            raise serializers.ValidationError("User with this username does not exist.")

        if not user.is_active:
            raise serializers.ValidationError("User is not active.")

        return value

    def create(self, validated_data):
        username = validated_data.pop('username')
        user = get_user_model().objects.get(username=username)
        employee = Employee.objects.create(user=user, **validated_data)
        return employee
        

class EmployeeSerializer(serializers.ModelSerializer):
    user = UserSimpleSerializer(read_only=True)
    store = StoreSimpleSerializer(read_only=True) 

    class Meta:
        model = Employee
        fields = ('id', 'user', 'store', 'is_admin', 'is_owner', 'hired_at')


class StoreOrdersListSerializer(serializers.ModelSerializer):
    product = ProductSimpleSerializer()
    total_price = serializers.SerializerMethodField()
    order = OrderSimpleSerializer()
	
    def get_total_price(self, order_item):
        total_price = order_item.get_total_price()
        return total_price

    class Meta:
        model = OrderItem
        fields = ('id', 'slug', 'order', 'product', 'quantity', 
                  'price', 'total_price', 'status', 'created_at', 'updated_at')
        

class StoreTransactionsListSerializer(serializers.ModelSerializer):
    related_order_item = serializers.SlugRelatedField(slug_field='slug', read_only=True)
    store = StoreSimpleSerializer(source='related_seller')

    class Meta:
        model = Transaction
        fields = ('id', 'uuid', 'transaction_type', 'amount',
                  'status', 'timestamp', 'related_order_item', 'store')


class AdminStoreTransactionsListSerializer(serializers.ModelSerializer):
    related_order_item = serializers.SlugRelatedField(slug_field='slug', read_only=True)
    related_seller = StoreSimpleSerializer()
    store = serializers.SerializerMethodField()

    class Meta:
        model = Transaction
        fields = ('id', 'uuid', 'transaction_type', 'amount', 'status', 'timestamp',
                  'related_order_item', 'related_seller', 'store')
        
    def get_store(self, obj):
        store = self.context['store']
        store_serializer = StoreSimpleSerializer(store)
        return store_serializer.data


class StoreProductListSerializer(ProductSerializer):
    total_orders = serializers.IntegerField()
    total_orders_done = serializers.IntegerField()
    total_orders_processing = serializers.IntegerField()
    total_orders_cancelled = serializers.IntegerField()
     
    class Meta:
        model = Product
        fields = ('id', 'slug', 'title', 'product_images', 'cosplay_character', 'seller',
	              'price', 'real_price', 'discount', 'product_type', 'in_stock',
				  'is_active', 'timestamp', 'reviews_count', 'average_score',
				  'total_orders', 'total_ordered_quantity', 'total_orders_done',
                  'total_orders_processing', 'total_orders_cancelled',)


class StoreProductDetailSerializer(ProductDetailSerializer):
    product_images = ProductImageSerializer(many=True, required=False)
    total_orders = serializers.IntegerField(read_only=True)
    total_orders_done = serializers.IntegerField(read_only=True)
    total_orders_processing = serializers.IntegerField(read_only=True)
    total_orders_cancelled = serializers.IntegerField(read_only=True)
    ordered_products = OrderItemSimpleSerializer(many=True, read_only=True)
     
    class Meta:
        model = Product
        fields = ('id', 'slug', 'title', 'product_images', 'cosplay_character', 'seller',
	              'price', 'real_price', 'discount', 'product_type', 'description', 
				  'in_stock', 'is_active', 'size', 'shoes_size', 'timestamp', 'reviews_count',
				  'average_score', 'total_orders', 'total_ordered_quantity',
                  'total_orders_done', 'total_orders_processing', 'total_orders_cancelled',
                  'reviews', 'ordered_products',)
        
    def validate_product_images(self, value):
        if len(value) > 10:
            raise serializers.ValidationError(f'You can upload a maximum of 10 images.')
        return value
        
    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Price must be a positive value.")
        return value
    
    def validate_discount(self, value):
        if value is not None and value <= 0:
            raise serializers.ValidationError("Discount must be a positive value.")
        return value
    
    def validate_in_stock(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError("Products amount in stock must be a positive value.")
        return value
