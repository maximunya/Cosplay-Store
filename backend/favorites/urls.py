from django.urls import path
from . import views


app_name = 'favorites'

urlpatterns = [    
    path('', views.FavoriteListView.as_view(), name='favorite-list'),
    path('manage/<int:product_id>/', views.manage_favorite_item, name='manage-favorite-item'),
]