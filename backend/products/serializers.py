from rest_framework import serializers
from .models import Product, ProductImage, Review, Answer


class ProductCreateSerializer(serializers.ModelSerializer):
	product_images = serializers.ListSerializer(child=serializers.ImageField(), write_only=True, required=False)

	class Meta:
		model = Product
		fields = ('title', 'product_images', 'price', 'discount', 
				  'description', 'cosplay_character', 'product_type',
				  'size', 'shoes_size', 'in_stock', 'is_active')

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


class ReviewCreateSerializer(serializers.ModelSerializer):
	class Meta:
		model = Review
		fields = ('text', 'score')

	
class AnswerCreateSerializer(serializers.ModelSerializer):
	class Meta:
		model = Answer
		fields = ('text',)
