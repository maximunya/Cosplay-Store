from django.db import models
from django.utils.text import slugify
from django.utils.crypto import get_random_string
from django.core.exceptions import ValidationError

from users.models import User
from fandoms.models import Character
from stores.models import Store


PRODUCT_TYPE_CHOICES = (
	('Full Set', 'Full Set'),
	('Clothes', 'Clothes'),
	('Wig', 'Wig'),
	('Shoes', 'Shoes'),
	('Lenses', 'Lenses'),
	('Details', 'Details'),
	('Others', 'Others')
)

PRODUCT_SIZE_CHOICES = (
	('XXS', 'XXS'),
	('XS', 'XS'),
	('S', 'S'),
	('M', 'M'),
	('L', 'L'),
	('XL', 'XL'),
	('XXL', 'XXL'),
	('One Size', 'One Size'),
)

SHOES_SIZE_CHOICES = (
	('35', '35'),
	('36', '36'),
	('37', '37'),
	('38', '38'),
	('39', '39'),
	('40', '40'),
	('41', '41'),
	('42', '42'),
	('43', '43'),
	('44', '44'),
	('45', '45'),
)


SCORE_CHOICES = (
    (1, '1'),
    (2, '2'),
    (3, '3'),
    (4, '4'),
    (5, '5'),
)


class Product(models.Model):
	"""Product model"""
	slug = models.SlugField(unique=True, allow_unicode=True, max_length=255, editable=False)
	seller = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='store_products')
	title = models.CharField(max_length=255)
	description = models.TextField(max_length=1000)
	price = models.PositiveIntegerField()
	discount = models.PositiveIntegerField(null=True, blank=True)
	cosplay_character = models.ForeignKey(Character, on_delete=models.CASCADE, related_name='products')
	product_type = models.CharField(
		max_length=50,
		choices=PRODUCT_TYPE_CHOICES
	)
	size = models.CharField(
		max_length=8, null=True,
		blank=True, choices=PRODUCT_SIZE_CHOICES
	)
	shoes_size = models.CharField(
		max_length=2, null=True,
		blank=True, choices=SHOES_SIZE_CHOICES
	)
	timestamp = models.DateTimeField(auto_now_add=True)
	in_stock = models.PositiveIntegerField(null=True, blank=True)
	is_active = models.BooleanField(default=True)

	def __str__(self):
		return self.title

	def get_real_price(self):
		if self.discount:
			discount = self.discount / 100
			return self.price - round((self.price * discount))
		return self.price
	
	def save(self, *args, **kwargs):
		if self.in_stock is not None and self.in_stock == 0:
			self.is_active = False

		if not self.slug:
			formatted_slug = f'{slugify(self.title, allow_unicode=True)[:100]}-{get_random_string(length=10, allowed_chars="1234567890")}'
			self.slug = formatted_slug
		return super().save(*args, **kwargs)


class ProductImage(models.Model):
	"""Product Image model"""
	def get_upload_to(instance, filename):
		product_id = instance.product.id
		return f"product_images/product_{product_id}/{filename}"
	
	product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_images')
	image = models.ImageField(
		upload_to=get_upload_to,
		default="product_images/no-photo-available-icon-20.jpg"
	)

	def __str__(self):
		return self.image.url

	def save(self, *args, **kwargs):
		if ProductImage.objects.filter(product=self.product).count() < 10:
			return super().save(*args, **kwargs)
		else:
			raise ValidationError('The limit is 10 images only.')


class Review(models.Model):
	"""Review model"""
	customer = models.ForeignKey(User, on_delete=models.CASCADE)
	product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
	score = models.PositiveSmallIntegerField(choices=SCORE_CHOICES)
	text = models.TextField(max_length=1000)
	timestamp = models.DateTimeField(auto_now_add=True)
	edited = models.DateTimeField(auto_now=True)

	def __str__(self):
		return f'{self.customer} - {self.score}* - {self.text}'
	

class Answer(models.Model):
	'''Answer model'''
	review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='answers')
	seller = models.ForeignKey(Store, on_delete=models.CASCADE)
	text = models.TextField(max_length=1000)
	timestamp = models.DateTimeField(auto_now_add=True)
	edited = models.DateTimeField(auto_now=True)

	def __str__(self):
		return f'{self.seller} - {self.text}'

