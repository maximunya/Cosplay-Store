from rest_framework import serializers

from common.serializers import ProductSerializer, FandomSerializer

from .models import Fandom, Character


class FandomCreateSerializer(serializers.ModelSerializer):
	class Meta:
		model = Fandom
		fields = ('name', 'fandom_type', 'image')


class CharacterCreateSerializer(serializers.ModelSerializer):
	class Meta:
		model = Character
		fields = ('name', 'image')


class FandomListSerializer(serializers.ModelSerializer):
	characters_count = serializers.IntegerField(read_only=True)
	total_fandom_products_count = serializers.IntegerField(read_only=True)

	class Meta:
		model = Fandom
		fields = ('id', 'slug', 'name', 'fandom_type', 'image',
				  'characters_count', 'total_fandom_products_count')


class CharacterListSerializer(serializers.ModelSerializer):
	fandom = FandomSerializer(read_only=True)
	products_count = serializers.IntegerField(read_only=True)

	class Meta:
		model = Character
		fields = ('id', 'slug', 'name', 'fandom', 'image', 'products_count')


class CharacterProductsCountSerializer(CharacterListSerializer):
	class Meta(CharacterListSerializer.Meta):
		fields = ('id', 'slug', 'name', 'image', 'products_count')


class FandomDetailSerializer(serializers.ModelSerializer):
	characters = CharacterProductsCountSerializer(many=True, read_only=True)
	characters_count = serializers.IntegerField(read_only=True)
	total_fandom_products_count = serializers.IntegerField(read_only=True)
	slug = serializers.SlugField(read_only=True)

	class Meta:
		model = Fandom
		fields = ('id', 'slug', 'name', 'fandom_type', 
				  'image', 'characters_count', 
				  'total_fandom_products_count', 'characters',)


class CharacterDetailSerializer(serializers.ModelSerializer):
	fandom = FandomSerializer(read_only=True)
	products_count = serializers.IntegerField(read_only=True)
	products = ProductSerializer(many=True, read_only=True)
	slug = serializers.SlugField(read_only=True)

	class Meta:
		model = Character
		fields = ('id', 'slug', 'name', 'fandom', 'image',
			      'products_count', 'products')





