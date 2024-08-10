from rest_framework import serializers

from common.serializers import UserSimpleSerializer, StoreSimpleSerializer

from .models import Card, Transaction


class CardCreateSerializer(serializers.ModelSerializer):
	class Meta:
		model = Card
		fields = ('name', 'card_number')

	def validate_card_number(self, value):
		if not value.isdigit() or len(value) != 16:
			raise serializers.ValidationError("Invalid card number.")
		return value
	

class CardSimpleSerializer(serializers.ModelSerializer):
	class Meta:
		model = Card
		fields = ('id', 'uuid', 'name', 'card_number', 'created_at')


class CardUserSerializer(serializers.ModelSerializer):
	user = UserSimpleSerializer(many=False, read_only=True)

	class Meta:
		model = Card
		fields = ('id', 'uuid', 'name', 'card_number', 'created_at', 'user')


class TransactionSimpleSerializer(serializers.ModelSerializer):
	related_order = serializers.SlugRelatedField(slug_field='slug', read_only=True)

	class Meta:
		model = Transaction
		fields = ('id', 'uuid', 'transaction_type', 'amount', 
				  'timestamp', 'status', 'related_order',)


class TransactionListSerializer(serializers.ModelSerializer):
	card = CardSimpleSerializer(many=False, read_only=True)
	related_order = serializers.SlugRelatedField(slug_field='slug', read_only=True)

	class Meta:
		model = Transaction
		fields = ('id', 'uuid', 'card', 'transaction_type', 'amount', 
				  'timestamp', 'status', 'related_order',)


class TransactionDetailSerializer(serializers.ModelSerializer):
	card = CardSimpleSerializer(many=False, read_only=True)
	related_order = serializers.SlugRelatedField(slug_field='slug', read_only=True)
	related_order_item = serializers.SlugRelatedField(slug_field='slug', read_only=True)
	related_seller = StoreSimpleSerializer(many=False, read_only=True)

	class Meta:
		model = Transaction
		fields = ('id', 'uuid', 'card', 'transaction_type', 'amount', 'timestamp',
			      'status', 'related_order', 'related_order_item', 'related_seller')


class CardDetailSerializer(serializers.ModelSerializer):
	card_transactions = TransactionSimpleSerializer(many=True, read_only=True)

	class Meta:
		model = Card
		fields = ('id', 'uuid', 'name', 'card_number', 'balance', 'created_at', 'card_transactions')
		read_only_fields = ('id', 'uuid', 'card_number', 'balance', 'created_at', 'card_transactions')
