from django.urls import path
from . import views


app_name = 'fandoms'

urlpatterns = [
    path('', views.FandomListView.as_view(), name='fandom-list'),   
    path('create/', views.FandomCreateView.as_view(), name='fandom-create'),
    path('characters/', views.CharacterListView.as_view(),  name='character-list'),
    path('<slug:slug>/', views.FandomDetailView.as_view(), name='fandom-detail'),
    path('<slug:fandom_slug>/characters/create/', views.CharacterCreateView.as_view(), name='character-create'),
    path('<slug:fandom_slug>/characters/<slug:slug>/', views.CharacterDetailView.as_view(), name='character-detail'),
]