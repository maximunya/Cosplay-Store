from django.conf import settings
from .models import Product
from django.db.models import Count, Avg, Prefetch, Q


class Cart(object):
    '''Объект корзины'''
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get('cart')
        if not cart:
            cart = self.session['cart'] = {}
        self.cart = cart

    def add(self, product, quantity=1):
        # Добавление товара в корзину
        product_id = str(product.id)
        if product_id not in self.cart:
            self.cart[product_id] = {'quantity': 0, 'price': str(product.price)}
        self.cart[product_id]['quantity'] += quantity
        self.save()

    def remove(self, product):
        # Удаление товара из корзины
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
        self.save()

    def save(self):
        # Сохранение изменений в сессии
        self.session['cart'] = self.cart
        self.session.modified = True

    def get_cart_items(self):
        # Получить список словарей каждого товара из корзины пользоветаля
        product_ids = self.cart.keys()
        products = Product.objects.select_related('seller', 'cosplay_character__fandom').annotate(
                reviews_count=Count('reviews'),
                average_score=Avg('reviews__score')).filter(id__in=product_ids)

        for product in products:
            self.cart[str(product.id)]['product'] = product

        cart_items = []
        for item in self.cart.values():
            item['price'] = int(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            cart_items.append(item)

        return cart_items
    
    def __iter__(self):
        product_ids = self.cart.keys()
        products = Product.objects.select_related('seller', 'cosplay_character__fandom').annotate(
                reviews_count=Count('reviews'),
                average_score=Avg('reviews__score')).filter(id__in=product_ids)
        for product in products:
            self.cart[str(product.id)]['product'] = product

        for item in self.cart.values():
            item['price'] = int(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            yield item
    
    def __len__(self):
        # Получить общее количество товаров в корзине
        total_quantity = 0
        for item in self.cart.values():
            total_quantity += int(item['quantity'])
        return total_quantity
    
    def clear(self):
        # Очистка корзины
        del self.cart
        self.session.modified = True