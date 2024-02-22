from django.db import models
from django.db.utils import IntegrityError
from django.utils.crypto import get_random_string

from django.core.validators import MinLengthValidator

from users.models import User
from products.models import Product


ORDER_STATUS_CHOICES = (
	(0, 'Cancelled'),
	(1, 'Created'),
	(2, 'Paid'),
	(3, 'Processing'),
	(4, 'Done'),
)

ORDER_ITEM_STATUS_CHOICES = (
	(0, 'Cancelled'),
	(1, 'Created'),
	(2, 'Paid'),
	(3, 'Sent'),
	(4, 'Received'),
)


class Order(models.Model):
	"""Order model"""
	slug = models.SlugField(unique=True, allow_unicode=True, max_length=13, editable=False)
	customer = models.ForeignKey(User, on_delete=models.PROTECT, null=True, blank=True)
	name = models.CharField(max_length=100, blank=False, null=False)
	phone_number = models.CharField(max_length=12, blank=False, null=False,
								 	validators=[MinLengthValidator(11, 'Incorrect phone number format.')])
	email = models.EmailField(blank=False, null=False)
	address = models.ForeignKey('users.Address', on_delete=models.PROTECT)
	card = models.ForeignKey('cards.Card', on_delete=models.PROTECT)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	total_order_price = models.PositiveIntegerField()
	status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, blank=False, null=False)

	def save(self, *args, **kwargs):
		if not self.slug:
			while True:
				digits_string = get_random_string(length=12, allowed_chars='1234567890')
				self.slug = digits_string[:8] + '-' + digits_string[8:]
				try:
					super(Order, self).save(*args, **kwargs)
				except IntegrityError:
					continue
				break
		else:
			super(Order, self).save(*args, **kwargs)

	def get_order_price(self):
		return sum(order_item.get_total_price() for order_item in self.order_items.all())
	
	def __str__(self):
		return self.slug
	

class OrderItem(models.Model):
	"""Order Product model"""
	slug = models.SlugField(unique=True, allow_unicode=True, max_length=10, editable=False)
	product = models.ForeignKey(Product, on_delete=models.PROTECT, 
							    related_name='ordered_products')
	order = models.ForeignKey(
		Order, on_delete=models.CASCADE,
		related_name='order_items'
	)
	quantity = models.PositiveIntegerField(default=1)
	status = models.CharField(max_length=20, choices=ORDER_ITEM_STATUS_CHOICES, blank=False, null=False)
	price = models.PositiveIntegerField()
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ['status', '-created_at']

	def __str__(self):
		return f'{self.product.title}: {self.quantity}'

	def get_total_price(self):
		return self.quantity * self.price
	
	def save(self, *args, **kwargs):
		if not self.slug:
			while True:
				self.slug = get_random_string(length=10, allowed_chars='1234567890')
				try:
					super(OrderItem, self).save(*args, **kwargs)
				except IntegrityError:
					continue
				break
		else:
			super(OrderItem, self).save(*args, **kwargs)

		



