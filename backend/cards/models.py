import uuid

from django.db import models
from django.core.exceptions import ValidationError

from users.models import User
from orders.models import OrderItem, Order
from stores.models import Store


class Card(models.Model):
    """Card model"""
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=255, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cards', blank=True, null=True)
    card_number = models.CharField(max_length=16, blank=False, null=False)
    balance = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(blank=True, auto_now_add=True)

    def __str__(self):
        return f'{self.card_number}'

    def save(self, *args, **kwargs):
        if self.user:
            if Card.objects.filter(user=self.user).count() < 5:
                return super(Card, self).save(*args, **kwargs)
            else:
                raise ValidationError('The limit is 5 credit cards only.')
        return super(Card, self).save(*args, **kwargs)

    class Meta:
        unique_together = ('user', 'card_number')
        ordering = ['created_at']


class Transaction(models.Model):
    """Transaction model"""
    TRANSACTION_TYPES = (
        ('Deposit', 'Deposit'),
        ('Purchase', 'Purchase'),
        ('Sale', 'Sale'),
        ('Commission', 'Commission'),
    )

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    card = models.ForeignKey(Card, on_delete=models.SET_NULL, related_name='card_transactions', null=True, blank=True)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    amount = models.PositiveIntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)
    related_order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True)
    related_order_item = models.ForeignKey(OrderItem, on_delete=models.SET_NULL, null=True, blank=True)
    related_seller = models.ForeignKey(Store, on_delete=models.SET_NULL, related_name='seller_transactions', null=True,
                                       blank=True)
    status = models.CharField(default="Success", null=False, blank=False)

    def __str__(self):
        return f'{self.transaction_type} - {self.amount}'

    class Meta:
        ordering = ['-timestamp']
