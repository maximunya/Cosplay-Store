from rest_framework import permissions
from django.shortcuts import get_object_or_404

from .models import Card


class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user
    

class CanSeeTransaction(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if obj.transaction_type in ['Purchase', 'Deposit']:
            return obj.card.user == request.user
        
        if obj.transaction_type in ['Sale', 'Comission']:
            return request.user in obj.related_seller.employees
    

class CanCreateDeposit(permissions.BasePermission):
    def has_permission(self, request, view):
        card_uuid = view.kwargs.get('card_uuid')
        card = get_object_or_404(Card, uuid=card_uuid)

        if card.user is None and not request.user.is_authenticated:
            return True
        return card.user == request.user