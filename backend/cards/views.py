from django.db import transaction
from django.shortcuts import get_object_or_404

from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes

from common.serializers import CardListSerializer

from .serializers import (
    CardDetailSerializer, 
    CardCreateSerializer,
    TransactionListSerializer,
    TransactionDetailSerializer
)
from .models import Card, Transaction
from .permissions import IsOwner, CanSeeTransaction, CanCreateDeposit




class CardCreateView(generics.CreateAPIView):
    serializer_class = CardCreateSerializer
    permission_classes = (IsAuthenticated,)

    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(user=user)
        

class CardListView(generics.ListAPIView):
    serializer_class = CardListSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        return Card.objects.select_related('user').filter(user=user)


class CardDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CardDetailSerializer
    permission_classes = (IsOwner,)
    queryset = Card.objects.select_related('user').prefetch_related('card_transactions').all()
    lookup_field = 'uuid'


class TransactionDetailView(generics.RetrieveAPIView):
    serializer_class = TransactionDetailSerializer
    permission_classes = (CanSeeTransaction,)
    queryset = Transaction.objects.select_related('card__user',
                                                  'related_order',
                                                  'related_order_item',
                                                  'related_seller').all()
    lookup_field = 'uuid'


class TransactionListView(generics.ListAPIView):
    serializer_class = TransactionListSerializer
    permission_classes = (IsAuthenticated,)
    
    def get_queryset(self):
        user = self.request.user
        return Transaction.objects.select_related('card__user').filter(card__user=user)


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