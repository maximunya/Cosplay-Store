import uuid
import json

from django.db import transaction
from django.db.models import Prefetch
from django.shortcuts import get_object_or_404
from django.conf import settings

from rest_framework import generics, status, filters
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django_filters.rest_framework import DjangoFilterBackend
from yookassa import Configuration, Payment

from common.serializers import CardListSerializer

from .serializers import (
    CardDetailSerializer,
    CardCreateSerializer,
    TransactionListSerializer,
    TransactionDetailSerializer,
    TransactionSimpleSerializer
)
from .permissions import IsOwner, CanSeeTransaction, CanCreateDeposit
from .models import Card, Transaction

Configuration.account_id = settings.YOOKASSA_SHOP_ID
Configuration.secret_key = settings.YOOKASSA_SECRET_KEY


class CardCreateView(generics.CreateAPIView):
    serializer_class = CardCreateSerializer
    permission_classes = (IsAuthenticated,)

    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(user=user)


class CardListView(generics.ListAPIView):
    serializer_class = CardListSerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filterset_fields = {'balance': ['gt', 'lt', 'exact'], }
    ordering = ['-balance', 'created_at']
    ordering_fields = ['balance', 'created_at', 'name']

    def get_queryset(self):
        user = self.request.user
        return Card.objects.select_related('user').filter(user=user)


class CardDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CardDetailSerializer
    permission_classes = (IsOwner,)
    lookup_field = 'uuid'
    filter_fields = [
        'transaction_type', 'amount',
        'amount__gt', 'amount__lt', 'status'
    ]
    ordering_fields = [
        'timestamp', 'amount', 'status', 'transaction_type',
        '-timestamp', '-amount', '-status', '-transaction_type'
    ]

    def get_queryset(self):
        filters = {k: v for k, v in self.request.query_params.items() if k in self.filter_fields}
        order_by = self.request.query_params.get('ordering', '-timestamp')
        ordering = order_by if order_by in self.ordering_fields else '-timestamp'
        return Card.objects.select_related('user').prefetch_related(
            Prefetch('card_transactions', queryset=Transaction.objects.filter(**filters).order_by(ordering))).all()

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        transactions = self.object.card_transactions.all()

        page = self.paginate_queryset(transactions)
        if page is not None:
            serializer = CardDetailSerializer(self.object)
            data = serializer.data
            data['card_transactions'] = TransactionSimpleSerializer(page, many=True).data
            return self.get_paginated_response(data)

        serializer = CardDetailSerializer(self.object, context={'request': request})
        return Response(serializer.data)


class TransactionDetailView(generics.RetrieveAPIView):
    serializer_class = TransactionDetailSerializer
    permission_classes = (CanSeeTransaction,)
    lookup_field = 'uuid'
    queryset = Transaction.objects.select_related(
        'card__user', 'related_order',
        'related_order_item', 'related_seller').all()


class TransactionListView(generics.ListAPIView):
    serializer_class = TransactionListSerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    ordering = ['-timestamp']
    filterset_fields = {
        'transaction_type': ['exact'],
        'card__name': ['exact'],
        'amount': ['gt', 'lt', 'exact'],
        'status': ['exact']
    }
    ordering_fields = [
        'amount', 'timestamp', 'status',
        'transaction_type', 'card__name'
    ]

    def get_queryset(self):
        user = self.request.user
        return Transaction.objects.select_related(
            'card__user').filter(card__user=user)


@api_view(['POST'])
@permission_classes([CanCreateDeposit])
@transaction.atomic
def create_deposit(request, card_uuid, amount):
    user = request.user
    if amount > 0:
        amount_with_comission = round(amount * 1.035)
        card = get_object_or_404(Card, uuid=card_uuid)
        transaction = Transaction.objects.create(card=card,
                                                 transaction_type='Deposit',
                                                 amount=amount,
                                                 status="Pending")
        try:
            payment = Payment.create({
                "amount": {
                    "value": str(amount_with_comission),
                    "currency": "RUB"
                },
                "payment_method_data": {
                    "type": "bank_card"
                },
                "capture": True,
                "test": True,
                "refundable": False,
                "metadata": {
                    'transaction_uuid': str(transaction.uuid),
                    'user_id': user.id,
                    'card_uuid': str(card_uuid),
                },
                "confirmation": {
                    "type": "redirect",
                    "return_url": f"http://localhost:8000/api/cards/{card_uuid}"
                },
                "description": f"Deposit create: User: {user.username} - Card: ****{card.card_number[12:]} -  Amount: {amount} RUB",
            }, uuid.uuid4())

            redirect_url = payment.confirmation.confirmation_url
            print(redirect_url)
            return Response({'redirect_url': redirect_url}, status=status.HTTP_302_FOUND)

        except Exception as e:
            print(f"Error creating deposit: {e}")
            return Response({'status': 'Error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return Response({'error': 'Deposit amount cannot be non-positive or equals 0.'},
                        status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@transaction.atomic
def handle_payment_callback(request):
    response = json.loads(request.body)
    print(response)

    transaction = get_object_or_404(Transaction, uuid=response['object']['metadata']['transaction_uuid'])
    card = get_object_or_404(Card, uuid=response['object']['metadata']['card_uuid'])

    if response['event'] == 'payment.succeeded':
        amount = response['object']['income_amount']['value']
        card.balance += int(float(amount))
        card.save()

        transaction.status = "Success"
        transaction.save()

        return Response({'status': 'Success'}, status=status.HTTP_200_OK)

    if response['event'] == 'payment.canceled':
        transaction.status = "Canceled"
        transaction.save()
        return Response({'status': 'Canceled'}, status=status.HTTP_200_OK)

    else:
        print(response)
        return Response({'status': 'Error'}, status=status.HTTP_400_BAD_REQUEST)
