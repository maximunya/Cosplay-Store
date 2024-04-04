from django.db import transaction
from django.db.models import (
    Count, Avg, Q, Prefetch, Sum, FloatField,
    F, ExpressionWrapper, IntegerField, Case, When
)
from django.db.models.functions import Coalesce
from django.shortcuts import get_object_or_404

from rest_framework import generics, status, filters, parsers
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django_filters.rest_framework import DjangoFilterBackend
from django_elasticsearch_dsl.search import Search

from products.models import Product, Review, ProductImage
from products.serializers import ProductCreateSerializer, AnswerCreateSerializer
from orders.models import OrderItem, ORDER_ITEM_STATUS_CHOICES
from cards.models import Transaction
from common.serializers import StoreListSerializer

from .models import Store, Employee
from . import serializers
from . import permissions
from .tasks import (
    send_order_item_sent_notifications,
    send_order_item_received_notifications,
    send_order_item_cancelled_notifications,
    update_full_order_status
)


class StoreCreateView(generics.CreateAPIView):
    serializer_class = serializers.StoreCreateSerializer
    permission_classes = (IsAuthenticated,)
    queryset = Store.objects.select_related('owner').all()

    def perform_create(self, serializer):
        user = self.request.user     
        store = serializer.save(owner=user)


class StoreDetailPrivateView(generics.RetrieveUpdateAPIView):
    serializer_class = serializers.StoreDetailPrivateSerializer
    permission_classes = (permissions.IsOwnerOrStoreAdminOrAdminReadOnly,)
    queryset = Store.objects.select_related('owner').all()
    lookup_field = 'slug'


class StoreDeleteView(generics.DestroyAPIView):
    serializer_class = serializers.StoreDetailPrivateSerializer
    permission_classes = (permissions.IsOwnerOrAdminUser,)
    queryset = Store.objects.select_related('owner').all()
    lookup_field = 'slug'            


class StoreDetailPublicView(generics.RetrieveAPIView):
    serializer_class = serializers.StoreDetailPublicSerializer
    lookup_field = 'slug'
    ordering_fields = [
        'timestamp', 'average_score', 'total_ordered_quantity',
        'reviews_count', 'actual_price', 'discount', 'title', 'in_stock',
        '-timestamp', '-average_score', '-total_ordered_quantity',
        '-reviews_count', '-actual_price', '-discount', '-title', '-in_stock'
    ]
    filter_fields = [
        'average_score__gt', 'actual_price__gt', 'actual_price__lt',
        'discount__gt', 'cosplay_character__name', 'product_type',
        'cosplay_character__fandom__name', 'total_ordered_quantity__gt',
        'cosplay_character__fandom__fandom_type', 'size', 'shoes_size'
    ]
    search_fields = [
        'title', 'description', 'cosplay_character.name',
        'cosplay_character.fandom.name', 'product_type',
        'cosplay_character.fandom.fandom_type', 'size', 'shoes_size',
    ]

    def get_queryset(self):
        search_query = self.request.query_params.get('q', '')
        filters = {k: v for k, v in self.request.query_params.items() if k in self.filter_fields}
        order_by = self.request.query_params.get('ordering', '-total_ordered_quantity')
        ordering = order_by if order_by in self.ordering_fields else '-total_ordered_quantity'

        search = Search(index='products').extra(size=100)

        if search_query:
            search = search.query("multi_match",
                                  query=search_query,
                                  fields=self.search_fields,
                                  fuzziness="auto")
        
        results = search.execute()
        product_ids = [hit.id for hit in results]

        filters['pk__in'] = product_ids

        return Store.objects.prefetch_related(
            Prefetch(
                'store_products',
                queryset=Product.objects.select_related('seller', 'cosplay_character__fandom'
                    ).prefetch_related('product_images').annotate(
                        reviews_count=Count('reviews', distinct=True),
                        average_score=Coalesce(Avg('reviews__score'), 0, output_field=FloatField()),
                        total_ordered_quantity=Coalesce(Sum('ordered_products__quantity'), 0),
                        actual_price=Case( 
                            When(discount__gt=0, then=F('price') - (F('price') * F('discount') / 100)),
                            default=F('price'),
                            output_field=FloatField()
                        )
                    ).filter(is_active=True, **filters).order_by(ordering, '-timestamp')
            )
            ).annotate(
                products_count=Count('store_products', filter=Q(store_products__is_active=True)),
                store_average_score=Avg('store_products__reviews__score')
            ).all()
    
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        products = self.object.store_products.all()

        page = self.paginate_queryset(products)
        if page is not None:
            serializer = serializers.StoreDetailPublicSerializer(self.object)
            data = serializer.data
            data['store_products'] = serializers.ProductSerializer(page, many=True).data
            return self.get_paginated_response(data)

        serializer = serializers.StoreDetailPublicSerializer(self.object, context={'request': request})
        return Response(serializer.data)
    

class StoreListView(generics.ListAPIView):
    serializer_class = StoreListSerializer
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter)
    filterset_fields = {'is_verified': ['exact'], 'organization_type': ['exact']}
    ordering = ['-is_admin_store', '-is_verified', 'name']
    ordering_fields = ['is_verified', 'name', 'products_count', 'store_average_score']
    search_fields = ['name', 'organization_name']
    queryset = Store.objects.annotate(
        products_count=Count('store_products', filter=Q(store_products__is_active=True)),
        store_average_score=Coalesce(Avg('store_products__reviews__score'), 0, output_field=FloatField())).all()
    

class StoreTransactionListView(generics.ListAPIView):
    permission_classes = (permissions.IsEmployee,)
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filterset_fields = {
        'transaction_type': ['exact'],
        'amount': ['gt', 'lt', 'exact'],
        'status': ['exact']
    }
    ordering = ['-timestamp']
    ordering_fields = ['amount', 'timestamp', 'status', 'transaction_type']

    def get_queryset(self):
        store = self.store
        if store.is_admin_store:
            return Transaction.objects.select_related(
                'card__user', 'related_order_item__product__cosplay_character__fandom', 'related_seller'
                ).prefetch_related('related_order_item__product__product_images'
                ).filter(Q(related_seller=store) | Q(transaction_type="Comission"))
        else:
            return Transaction.objects.select_related(
                'card__user', 'related_order_item__product__cosplay_character__fandom', 'related_seller'
                ).prefetch_related('related_order_item__product__product_images'
                ).filter(related_seller=store)

    def get_serializer_class(self, *args, **kwargs):
        store = self.store
        if store.is_admin_store:
            return serializers.AdminStoreTransactionsListSerializer
        else:
            return serializers.StoreTransactionsListSerializer
        
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['store'] = self.store
        return context


class EmployeeCreateView(generics.CreateAPIView):
    serializer_class = serializers.EmployeeCreateSerializer
    permission_classes = (permissions.IsOwnerOrStoreAdmin,)

    def perform_create(self, serializer):
        store = self.store
        new_employee = serializer.save(store=store)


class EmployeeListView(generics.ListAPIView):
    serializer_class = serializers.EmployeeSerializer
    permission_classes = (permissions.IsEmployee,)
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter)
    filterset_fields = {
        'is_admin': ['exact'],
        'hired_at': ['year', 'year__lt', 'year__gt']
    }
    ordering = ['-is_owner', '-is_admin', 'user__username']
    ordering_fields = ['hired_at', 'is_admin', 'user__username']
    search_fields = ['user__username', 'user__first_name', 'user__last_name']

    def get_queryset(self):
        store = self.store
        return Employee.objects.select_related(
            'user', 'store').filter(store=store)
    

class EmployeeDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = serializers.EmployeeSerializer
    permission_classes = (permissions.IsOwnerOrStoreAdminOrEmployeeReadOnly,)
    lookup_field = 'user__username'
    lookup_url_kwarg = 'username'

    def get_queryset(self):
        store = self.store
        return Employee.objects.select_related('user', 'store').filter(store=store)
    

class StoreOrderListView(generics.ListAPIView):
    serializer_class = serializers.StoreOrdersListSerializer
    permission_classes = (permissions.IsEmployee,)
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filterset_fields = {
        'created_at': ['year', 'month', 'day'],
        'status': ['exact']
    }
    ordering = ['-created_at']
    ordering_fields = ['created_at', 'updated_at',
                       'annotated_total_price', 'status']

    def get_queryset(self):
        store = self.store
        return OrderItem.objects.select_related(
            'product__cosplay_character__fandom',
            'product__seller', 'order__customer', 'order__address'
            ).prefetch_related('product__product_images'
            ).filter(product__seller=store).annotate(
                annotated_total_price=ExpressionWrapper(
                    F('price') * F('quantity'), output_field=IntegerField()))


class StoreProductListView(generics.ListAPIView):
    serializer_class = serializers.StoreProductListSerializer
    permission_classes = (permissions.IsEmployee,)
    filter_backends = (filters.OrderingFilter,)
    filter_fields = [
    'product_type', 'size', 'shoes_size', 'average_score',
    'average_score__gt', 'average_score__lt', 'reviews_count',
    'reviews_count__gt', 'reviews_count__lt', 'actual_price',
    'actual_price__gt', 'actual_price__lt', 'discount', 'discount__gt',
    'discount__lt', 'cosplay_character__name', 'cosplay_character__fandom__name',
    'cosplay_character__fandom__fandom_type', 'total_ordered_quantity',
    'total_ordered_quantity__gt', 'total_ordered_quantity__lt',
    'total_orders', 'total_orders__gt', 'total_orders__lt',
    'total_orders_done', 'total_orders_done__gt', 'total_orders_done__lt',
    'total_orders_processing', 'total_orders_processing__gt',
    'total_orders_processing__lt', 'total_orders_cancelled',
    'total_orders_cancelled__gt', 'total_orders_cancelled__lt'
    ]
    ordering = ['-is_active', '-total_orders_processing', '-timestamp']
    ordering_fields = [
        'timestamp', 'average_score', 'total_ordered_quantity',
        'reviews_count', 'actual_price', 'discount', 'title', 'in_stock',
        'total_orders', 'total_orders_done', 'total_orders_processing',
        'total_orders_cancelled'
    ]
    search_fields = [
        'title', 'description', 'cosplay_character.name',
        'cosplay_character.fandom.name', 'product_type',
        'cosplay_character.fandom.fandom_type', 'size', 'shoes_size',
    ]

    def get_queryset(self):
        store = self.store
        search_query = self.request.query_params.get('q', '')
        filters = {k: v for k, v in self.request.query_params.items() if k in self.filter_fields}

        search = Search(index='products').extra(size=1000)

        if search_query:
            search = search.query("multi_match",
                                  query=search_query,
                                  fields=self.search_fields,
                                  fuzziness="auto")
        
        results = search.execute()
        product_ids = [hit.id for hit in results]
        filters['pk__in'] = product_ids

        return Product.objects.select_related('cosplay_character__fandom', 'seller'
            ).prefetch_related('product_images').annotate(
                reviews_count=Count('reviews', distinct=True),
                average_score=Coalesce(Avg('reviews__score'), 0, output_field=FloatField()),
                total_ordered_quantity=Coalesce(Sum('ordered_products__quantity'), 0),
                total_orders=Count('ordered_products'),
                total_orders_done=Count('ordered_products', filter=Q(ordered_products__status=5)),
                total_orders_processing=Count('ordered_products', filter=Q(ordered_products__status__in=[1, 2, 3, 4])),
                total_orders_cancelled=Count('ordered_products', filter=Q(ordered_products__status=0)),
                actual_price=Case( 
                        When(discount__gt=0, then=F('price') - (F('price') * F('discount') / 100)),
                        default=F('price'),
                        output_field=FloatField()
                    )
            ).filter(seller=store, **filters)
    

class StoreProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = serializers.StoreProductDetailSerializer
    permission_classes = (permissions.IsOwnerOrStoreAdminOrEmployeeRetrieveUpdateOnly,)
    lookup_field = 'slug'

    def get_queryset(self):
        store = self.store
        return Product.objects.select_related('cosplay_character__fandom', 'seller'
                ).prefetch_related('reviews__customer',
                                   'reviews__answers__seller', 
                                   'product_images',
                                   'ordered_products'
                ).annotate(
                    reviews_count=Count('reviews', distinct=True),
                    average_score=Coalesce(Avg('reviews__score'), 0, output_field=FloatField()),
                    total_orders=Count('ordered_products'),
                    total_ordered_quantity=Coalesce(Sum('ordered_products__quantity'), 0),
                    total_orders_done=Count('ordered_products', filter=Q(ordered_products__status=5)),
                    total_orders_processing=Count('ordered_products', filter=Q(ordered_products__status__in=[1, 2, 3, 4])),
                    total_orders_cancelled=Count('ordered_products', filter=Q(ordered_products__status=0))
                ).filter(seller=store)
    
    def perform_update(self, serializer):
        product = self.get_object()
        product_images = serializer.validated_data.get('product_images', [])
        
        if product_images:
            product.product_images.all().delete()
            for image in product_images:
                ProductImage.objects.create(product=product, image=image)

        serializer.save()
    

class ProductCreateView(generics.CreateAPIView):
    serializer_class = ProductCreateSerializer
    permission_classes = (permissions.IsEmployee,)

    @transaction.atomic
    def perform_create(self, serializer):
        store = self.store
        product = serializer.save(seller=store)

        product_images = serializer.validated_data.get('product_images', [])

        if product_images:
            for image in product_images:
                ProductImage.objects.create(product=product, image=image)

    
class AnswerCreateView(generics.CreateAPIView):
    serializer_class = AnswerCreateSerializer
    permission_classes = (permissions.IsEmployee,)

    def perform_create(self, serializer):
        store = self.store

        review_id = self.kwargs['review_id']
        review = get_object_or_404(Review, pk=review_id, product__seller=store)

        answer = serializer.save(seller=store, review=review)


@api_view(['POST'])
@permission_classes([permissions.IsEmployee,])
@transaction.atomic
def update_order_status(request, slug, order_item_slug, new_status):
    store = get_object_or_404(Store, slug=slug)
    order_item = get_object_or_404(OrderItem.objects.select_related('order'), 
                                   slug=order_item_slug, 
                                   product__seller=store)
    order = order_item.order

    try:
        new_status = int(new_status)
    except (ValueError, TypeError):
        return Response({'error': 'Invalid status value.'}, status=status.HTTP_400_BAD_REQUEST)

    if new_status not in [0, 2, 3, 4]:
        return Response({'error': 'Invalid status value.'}, status=status.HTTP_400_BAD_REQUEST)

    if new_status == order_item.status:
        return Response({'error': 'The new status is the same as the current status of the order item.'},
                        status=status.HTTP_400_BAD_REQUEST)
    
    order_item.status = new_status
    order_item.save()

    if new_status == 3:
        send_order_item_sent_notifications.delay(order_item.id)
    if new_status == 4:
        send_order_item_received_notifications.delay(order_item.id)
    if new_status == 0:
        send_order_item_cancelled_notifications.delay(order_item.id)

    update_full_order_status.delay(order.id)

    return Response({'message': 'Order status updated successfully.'}, status=status.HTTP_200_OK)

