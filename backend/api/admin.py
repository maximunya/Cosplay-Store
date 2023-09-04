from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User, Product, Order, Favorite
from .models import OrderItem, Character, Fandom
from .models import CreditCard, ProductImage, Review


admin.site.register(User, UserAdmin)
admin.site.register(Product)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Character)
admin.site.register(Fandom)
admin.site.register(CreditCard)
admin.site.register(ProductImage)
admin.site.register(Review)
admin.site.register(Favorite)

