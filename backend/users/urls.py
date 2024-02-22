from django.urls import path
from . import views


app_name = 'users'

urlpatterns = [    
    path('', views.UserListView.as_view(), name='user-list'),
    path('inactive/', views.InactiveUserListView.as_view(), name='inactive-user-list'),
    path('inactive/<str:username>/', views.InactiveUserDetailView.as_view(), name='inactive-user-detail'),
    path('addresses/create/', views.AddressCreateView.as_view(), name='address-create'),
    path('addresses/', views.AddressListView.as_view(), name='address-list'),
    path('addresses/<uuid:uuid>/', views.AddressDetailView.as_view(), name='address-detail'),
    path('stores/', views.UserStoresListView.as_view(), name='user-stores-list'),
    path('<str:username>/', views.UserDetailView.as_view(), name='user-detail'),
]