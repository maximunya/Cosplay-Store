from django.contrib import admin

from .models import Product, Review, ProductImage, Answer


admin.site.register(Review)
admin.site.register(ProductImage)
admin.site.register(Answer)


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImageInline]

admin.site.register(Product, ProductAdmin)

