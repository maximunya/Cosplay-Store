from django.urls import path
from . import views


app_name = 'cards'

urlpatterns = [
    path('', views.CardListView.as_view(), name='card-list'), 
    path('create/', views.CardCreateView.as_view(), name='card-create'),
    path('<uuid:uuid>/', views.CardDetailView.as_view(), name='card-detail'),
    path('<uuid:card_uuid>/create-deposit/<int:amount>/', views.create_deposit, name='create-deposit'),
    path('transactions/', views.TransactionListView.as_view(), name='user-transaction-list'),
    path('transactions/<uuid:uuid>/', views.TransactionDetailView.as_view(), name='transaction-detail'),
]