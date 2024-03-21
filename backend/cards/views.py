from django.db import transaction
from django.db.models import Prefetch
from django.shortcuts import get_object_or_404

from rest_framework import generics, status, filters
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django_filters.rest_framework import DjangoFilterBackend

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
    filterset_fields = {'balance': ['gt', 'lt', 'exact'],}
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
def create_deposit(request, card_uuid, amount):
    if amount > 0:
        try:
            with transaction.atomic():
                card = get_object_or_404(Card, uuid=card_uuid)
                card.balance += amount
                card.save()
                Transaction.objects.create(card=card, 
                                           transaction_type='Deposit', 
                                           amount=amount)
            return Response({'status': 'Success'}, status=status.HTTP_201_CREATED)
        except Exception as e:
            print(f"Error creating deposit: {e}")
            return Response({'status': 'Error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return Response({'error': 'Deposit amount cannot be non-positive or equals 0.'}, status=status.HTTP_400_BAD_REQUEST)