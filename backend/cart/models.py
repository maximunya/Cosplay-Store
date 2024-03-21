from django.db import models

from django.core.exceptions import ValidationError

from users.models import User
from products.models import Product


class CartItem(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	product = models.ForeignKey(Product, on_delete=models.CASCADE)
	quantity = models.PositiveIntegerField(default=1)

	def get_total_price(self):
		return self.product.get_real_price() * self.quantity

	def save(self, *args, **kwargs):
		if CartItem.objects.filter(user=self.user).count() < 100:
			return super(CartItem, self).save(*args, **kwargs)
		else:
			raise ValidationError('The cart limit is 100 products only.')
		
	class Meta:
		ordering = ['-id']