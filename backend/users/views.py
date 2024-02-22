from django.contrib.auth import get_user_model

from rest_framework import generics
from rest_framework.permissions import IsAdminUser, IsAuthenticated

from stores.models import Employee
from common_serializers import UserSimpleSerializer

from . import serializers
from .permissions import IsOwnerOrAdminOrReadOnly, IsOwner
from .models import Address


User = get_user_model()


# User Views
class UserListView(generics.ListAPIView):
    serializer_class = UserSimpleSerializer
    queryset = User.objects.filter(is_active=True)


class InactiveUserListView(generics.ListAPIView):
    serializer_class = UserSimpleSerializer
    queryset = User.objects.filter(is_active=False)
    permission_classes = (IsAdminUser,)


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.filter(is_active=True)
    permission_classes = (IsOwnerOrAdminOrReadOnly,)
    lookup_field = 'username'

    def get_serializer_class(self):
        user = self.request.user
        if user.is_staff or user == self.get_object():
            return serializers.UserDetailPrivateSerializer
        return serializers.UserDetailPublicSerializer


class InactiveUserDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = serializers.UserDetailPrivateSerializer
    queryset = User.objects.filter(is_active=False)
    permission_classes = (IsAdminUser,)
    lookup_field = 'username'


# Address Views
class AddressCreateView(generics.CreateAPIView):
    serializer_class = serializers.AddressCreateSerializer
    permission_classes = (IsAuthenticated,)
    
    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(user=user) 


class AddressListView(generics.ListAPIView):
    serializer_class = serializers.AddressSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        return Address.objects.select_related('user').filter(user=user)
    

class AddressDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = serializers.AddressSerializer
    queryset = Address.objects.select_related('user').all()
    permission_classes = (IsOwner,)
    lookup_field = 'uuid'


class UserStoresListView(generics.ListAPIView):
    serializer_class = serializers.UserStoresListSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        return Employee.objects.select_related('store').filter(user=user)



