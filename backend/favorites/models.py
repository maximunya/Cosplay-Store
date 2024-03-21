from django.db import models

from django.core.exceptions import ValidationError

from users.models import User
from products.models import Product


class Favorite(models.Model):
	"""Favorite products model"""
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	product = models.ForeignKey(Product, on_delete=models.CASCADE)

	def __str__(self):
		return self.product

	def save(self, *args, **kwargs):
		if Favorite.objects.filter(user=self.user).count() < 500:
			return super(Favorite, self).save(*args, **kwargs)
		else:
			raise ValidationError('The limit is 500 favorite products only.')
		
	class Meta:
		unique_together = ('user', 'product')
		ordering = ['-id']

