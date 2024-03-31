from django.urls import path
from django.views.decorators.cache import cache_page

from . import views


app_name = 'fandoms'

urlpatterns = [
    path('', cache_page(60*5)(views.FandomListView.as_view()), name='fandom-list'),   
    path('create/', views.FandomCreateView.as_view(), name='fandom-create'),
    path('characters/', cache_page(60*5)(views.CharacterListView.as_view()),  name='character-list'),
    path('<slug:slug>/', cache_page(60*5)(views.FandomDetailView.as_view()), name='fandom-detail'),
    path('<slug:fandom_slug>/characters/create/', views.CharacterCreateView.as_view(), name='character-create'),
    path('<slug:fandom_slug>/characters/<slug:slug>/', cache_page(60*5)(views.CharacterDetailView.as_view()), name='character-detail'),
]