from django.shortcuts import get_object_or_404

from rest_framework import permissions

from orders.models import OrderItem

from .models import Product, Review


class IsSeller(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        employees = obj.seller.employees.all()
        employees_users = [employee.user for employee in employees]

        return request.user in employees_users       


class IsSellerOrAdminOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        if request.user and request.user.is_staff:
            return True

        employees = obj.seller.employees.all()
        employees_users = [employee.user for employee in employees]

        return request.user in employees_users
    

class IsCustomerOrAdminUser(permissions.BasePermission):
    def has_permission(self, request, view):
        product = get_object_or_404(Product, pk=view.kwargs['pk'], is_active=True)

        if request.user and not Review.objects.filter(product=product, customer=request.user).exists():
            if request.user.is_staff:
                return True
            
            order_items = OrderItem.objects.select_related('product', 'order__customer').filter(product=product)
            customers = [item.order.customer for item in order_items]

            return request.user in customers

    
class IsAuthorOrAdminOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        if request.user and request.user.is_staff and request.method in ('DELETE', 'GET', 'HEAD', 'OPTIONS'):
            return True
        
        return obj.customer == request.user
    

class IsSellerOrAdminUser(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user and request.user.is_staff:
            return True

        employees = obj.seller.employees.all()
        employees_users = [employee.user for employee in employees]

        return request.user in employees_users
    

class IsSellerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        employees = obj.seller.employees.all()
        employees_users = [employee.user for employee in employees]

        return request.user in employees_users

