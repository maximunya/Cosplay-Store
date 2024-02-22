from django.shortcuts import get_object_or_404
from rest_framework import permissions

from .models import Store


class IsOwnerOrStoreAdminOrAdminReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False
        
        if request.user == obj.owner:
            return True
    
        if obj.employees.filter(user=request.user, is_admin=True).exists():
            return True

        return (request.method in permissions.SAFE_METHODS and request.user.is_staff)
    

class IsOwnerOrAdminUser(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user == obj.owner:
            return True

        return request.user and request.user.is_staff
    

class IsEmployee(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        store = get_object_or_404(Store, slug=view.kwargs['slug'])
        view.store = store
        
        return store.employees.filter(user=request.user).exists()
    

class IsStoreEmployee(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False
        
        return obj.employees.filter(user=request.user).exists()
    

class IsOwnerOrStoreAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        store_slug = view.kwargs['slug']
        store = get_object_or_404(Store.objects.prefetch_related('employees'), slug=store_slug)
        view.store = store
        employees = store.employees

        if employees.filter(user=request.user, is_owner=True).exists():
            return True
        
        return employees.filter(user=request.user, is_admin=True).exists()
    

class IsOwnerOrStoreAdminOrEmployeeReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        store_slug = view.kwargs['slug']
        store = get_object_or_404(Store.objects.prefetch_related('employees'), slug=store_slug)
        view.store = store
        employees = store.employees

        if request.method in permissions.SAFE_METHODS and employees.filter(user=request.user).exists():
            return True
        
        if request.method == 'DELETE' and employees.filter(user=request.user, is_admin=True).exists():
            return True
        
        return employees.filter(user=request.user, is_owner=True).exists()
    

class IsOwnerOrStoreAdminOrEmployeeRetrieveUpdateOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        store_slug = view.kwargs['store_slug']
        store = get_object_or_404(Store.objects.prefetch_related('employees'), slug=store_slug)
        view.store = store
        employees = store.employees
        employee_methods = ('GET', 'HEAD', 'OPTIONS', 'PUT', 'PATCH')

        if request.method in employee_methods and employees.filter(user=request.user).exists():
            return True
        
        if employees.filter(user=request.user, is_admin=True).exists():
            return True
        
        return employees.filter(user=request.user, is_owner=True).exists()
        
 


    

