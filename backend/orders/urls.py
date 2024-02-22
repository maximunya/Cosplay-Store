from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('', views.OrderListView.as_view(), name='order-list'),   
    path('create/', views.OrderCreateView.as_view(), name='order-create'),
    path('<slug:slug>/', views.OrderDetailView.as_view(), name='order-detail'),
    path('items/<slug:slug>/', views.OrderItemView.as_view(), name='order-item'),
    path('<int:order_id>/payment-create/', views.create_order_payment, name='payment-create')
]