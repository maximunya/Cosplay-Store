from rest_framework import serializers

from djoser.serializers import (
    UserCreateSerializer,
    UserSerializer,
    UserCreatePasswordRetypeSerializer
)

from stores.models import Employee
from common.serializers import StoreSimpleSerializer

from .models import User, Address


class CustomUserCreateSerializer(UserCreateSerializer):
	class Meta(UserCreateSerializer.Meta):
		model = User
		fields = ('id', 'username', 'email', 'password')

	def validate_username(self, value):
		allowed_characters = {'_', '-'}
		
		if not all(char.isalnum() or char in allowed_characters for char in value):
			raise serializers.ValidationError("Username must consist of Latin letters, underscore (_), or hyphen (-).")
		if len(value) < 3:
			raise serializers.ValidationError("Username must be at least 3 characters long.")
		if value.isdigit():
			raise serializers.ValidationError("Username cannot consist only of digits.")
		if not value[0].isalpha():
			raise serializers.ValidationError("Username must start with a letter.")
		if not value[-1].isalnum():
			raise serializers.ValidationError("Username cannot end with special characters.")
		return value


class CustomUserCreatePasswordRetypeSerializer(UserCreatePasswordRetypeSerializer):
	class Meta(UserCreatePasswordRetypeSerializer.Meta):
		model = User
		fields = ('id', 'username', 'email', 'password')

	def validate_username(self, value):
		allowed_characters = {'_', '-'}
		
		if not all(char.isalnum() or char in allowed_characters for char in value):
			raise serializers.ValidationError("Username must consist of Latin letters, underscore (_), or hyphen (-).")
		if len(value) < 3:
			raise serializers.ValidationError("Username must be at least 3 characters long.")
		if value.isdigit():
			raise serializers.ValidationError("Username cannot consist only of digits.")
		if not value[0].isalpha():
			raise serializers.ValidationError("Username must start with a letter.")
		if not value[-1].isalnum():
			raise serializers.ValidationError("Username cannot end with special characters.")
		return value


class UserDetailPrivateSerializer(UserSerializer):
	age = serializers.SerializerMethodField()

	def get_age(self, user):
		return user.get_age()
	
	class Meta:
		model = User
		fields = ('id', 'username', 'email', 'first_name',
	    	 	  'last_name', 'birth_date', 'age', 'phone_number', 
			      'is_active', 'is_superuser', 'is_staff', 
			      'last_login', 'date_joined', 'profile_pic')
		read_only_fields = ('id', 'email', 'age', 'is_superuser', 
					        'is_staff', 'last_login', 'date_joined')
		
	def validate_username(self, value):
		allowed_characters = {'_', '-'}

		if not all(char.isalnum() or char in allowed_characters for char in value):
			raise serializers.ValidationError("Username must consist of Latin letters, underscore (_), or hyphen (-).")
		if len(value) < 3:
			raise serializers.ValidationError("Username must be at least 3 characters long.")
		if value.isdigit():
			raise serializers.ValidationError("Username cannot consist only of digits.")
		if not value[0].isalpha():
			raise serializers.ValidationError("Username must start with a letter.")
		if not value[-1].isalnum():
			raise serializers.ValidationError("Username cannot end with special characters.")
		return value
	
	def validate_first_name(self, value):
		if not value.isalpha():
			raise serializers.ValidationError("First name must consist only of letters.")
		return value
		
	def validate_last_name(self, value):
		if not value.isalpha():
			raise serializers.ValidationError("Last name must consist only of letters.")
		return value

	def validate_phone_number(self, value):
		if len(value) == 11 and value.isdigit():
			return value
		elif len(value) == 12 and value.startswith('+') and value[1:].isdigit():
			return value
		else:
			raise serializers.ValidationError("Incorrect phone number.")
		

class UserDetailPublicSerializer(UserSerializer):
	age = serializers.SerializerMethodField()

	def get_age(self, user):
		return user.get_age()
	
	class Meta:
		model = User
		fields = ('id', 'username', 'first_name', 
			      'last_name', 'birth_date', 'age', 
				  'is_active', 'is_staff', 'profile_pic')


class AddressCreateSerializer(serializers.ModelSerializer):
	class Meta:
		model = Address
		fields = ('id', 'name', 'address')


class AddressSerializer(serializers.ModelSerializer):
	class Meta:
		model = Address
		fields = ('id', 'uuid', 'name', 'address', 'created_at')
		read_only_fields = ('id', 'uuid', 'created_at')


class UserStoresListSerializer(serializers.ModelSerializer):
	store = StoreSimpleSerializer()

	class Meta:
		model = Employee
		fields = ('id', 'store', 'is_owner', 'is_admin', 'hired_at')
