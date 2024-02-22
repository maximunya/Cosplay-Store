from rest_framework import permissions

class IsCustomerOrAdminUser(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user and request.user.is_staff:
            return True

        if obj.customer:
            return request.user == obj.customer
        else:
            return True
        

class IsCustomerOrSellerOrAdminUser(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user and request.user.is_staff:
            return True

        if obj.product.seller.employees.filter(user=request.user).exists():
            return True

        if obj.order.customer:
            return request.user == obj.order.customer
        else:
            return True
