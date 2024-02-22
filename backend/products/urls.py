from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [    
    path('', views.ProductListView.as_view(), name='product-list'),
    path('<slug:slug>/', views.ProductDetailView.as_view(), name='product-detail'),
    path('<int:pk>/reviews/create/', views.ReviewCreateView.as_view(), name='review-create'),
    path('<int:product_id>/reviews/<int:pk>/', views.ReviewDetailView.as_view(), name='review-detail'),
    path('<int:product_id>/answers/<int:pk>/', views.AnswerDetailView.as_view(), name='answer-detail'),
]