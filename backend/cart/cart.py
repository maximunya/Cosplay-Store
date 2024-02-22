from django.conf import settings
from .models import Product
from django.db.models import Count, Avg, Sum


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
            self.cart[product_id] = {'quantity': 0}
        self.cart[product_id]['quantity'] += quantity
        self.save()
    
    def reduce(self, product, quantity=1):
        # Сокращение количества товара в корзине
        product_id = str(product.id)
        if product_id in self.cart:
            if self.cart[product_id]['quantity'] == quantity:
                return self.remove(product)
            else:
                self.cart[product_id]['quantity'] -= quantity
                self.save()
                return {"message": 'Product quantity in your cart was reduced.'}
        else:
            return {"error": 'There is no such product in your cart.'}

    def remove(self, product):
        # Удаление товара из корзины
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()
            return {"message": 'Product was deleted from your cart.'}
        else:
            return {"error": 'There is no such product in your cart.'}

    def save(self):
        # Сохранение изменений в сессии
        self.session['cart'] = self.cart
        self.session.modified = True


    def get_cart_items(self):
        # Получить список словарей каждого товара из корзины пользоветаля
        product_ids = self.cart.keys()
        products = Product.objects.annotate(
                reviews_count=Count('reviews'),
                average_score=Avg('reviews__score'),
                total_ordered_quantity=Sum('ordered_products__quantity')
            ).prefetch_related('reviews', 'product_images'
            ).select_related('seller', 'cosplay_character__fandom'
            ).filter(is_active=True, id__in=product_ids)

        for product in products:
            self.cart[str(product.id)]['product'] = product

        cart_items = []
        for item in self.cart.values():
            item['price'] = item['product'].get_real_price()
            item['total_price'] = item['price'] * item['quantity']
            cart_items.append(item)
        return cart_items
    
    def get_total_cart_price(self):
        return sum(item['total_price'] for item in self.get_cart_items())
    
    def __iter__(self):
        product_ids = self.cart.keys()
        products = Product.objects.annotate(
                reviews_count=Count('reviews'),
                average_score=Avg('reviews__score'),
                total_ordered_quantity=Sum('ordered_products__quantity')
            ).prefetch_related('reviews', 'product_images'
            ).select_related('seller', 'cosplay_character__fandom'
            ).filter(is_active=True, id__in=product_ids)
        
        for product in products:
            self.cart[str(product.id)]['product'] = product

        for item in self.cart.values():
            item['price'] = item['product'].get_real_price()
            item['total_price'] = item['price'] * item['quantity']
            yield item
    
    def __len__(self):
        # Получить общее количество товаров в корзине
        return sum(item['quantity'] for item in self.cart.values())
    
    def clear(self):
        # Очистка корзины
        del self.session['cart']
        self.session.modified = True


