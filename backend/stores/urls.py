from django.urls import path
from . import views


app_name = 'stores'

urlpatterns = [    
    path('', views.StoreListView.as_view(), name='store-list'),
    path('create/', views.StoreCreateView.as_view(), name='store-create'),
    path('<slug:slug>/', views.StoreDetailPublicView.as_view(), name='store-detail-public'),
    path('<slug:slug>/edit/', views.StoreDetailPrivateView.as_view(), name='store-detail-private'),
    path('<slug:slug>/delete/', views.StoreDeleteView.as_view(), name='store-delete'),
    path('<slug:slug>/employees/', views.EmployeeListView.as_view(), name='employee-list'),
    path('<slug:slug>/employees/create/', views.EmployeeCreateView.as_view(), name='employee-create'),
    path('<slug:slug>/employees/<str:username>/', views.EmployeeDetailView.as_view(), name='employee-detail'),
    path('<slug:slug>/orders/', views.StoreOrderListView.as_view(), name='store-order-list'),
    path('<slug:slug>/orders/<slug:order_item_slug>/update-status/<int:new_status>/', views.update_order_status),
    path('<slug:slug>/transactions/', views.StoreTransactionListView.as_view(), name='store-transaction-list'),
    path('<slug:slug>/products/', views.StoreProductListView.as_view(), name='store-product-list'),
    path('<slug:slug>/products/create/', views.ProductCreateView.as_view(), name='store-product-create'),
    path('<slug:store_slug>/products/<slug:slug>/', views.StoreProductDetailView.as_view(), name='store-product-detail'),
    path('<slug:slug>/reviews/<int:review_id>/answers/create/', views.AnswerCreateView.as_view(), name='store-answer-create'),
]