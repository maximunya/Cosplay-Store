from django.urls import path
from . import views


app_name = 'cart'

urlpatterns = [   
    path('', views.cart_list, name='cart-list'),
    path('add/<int:product_id>/<int:quantity>/', views.add_product_to_cart, name='add-to-cart'),
    path('delete/<int:product_id>/', views.delete_from_cart, name='delete-from-cart'),
    path('reduce/<int:product_id>/<int:quantity>/',
         views.reduce_product_quantity_in_cart,
         name='reduce-product-quantity-in-cart'),
]