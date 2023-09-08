from django.db import models

from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError


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

FANDOM_TYPE_CHOICES = (
	('Games', 'Games'),
	('Anime', 'Anime'),
	('Series', 'Series'),
	('Movies', 'Movies'),
	('Cartoons', 'Cartoons'),
	('Other', 'Other'),
)

ORDER_STATUS_CHOICES = (
	('Created', 'Created'),
	('Paid', 'Paid'),
	('Delivered', 'Delivered'),
	('Received', 'Received'),
)

LOW = 1
OK = 2
NORMAL = 3
GOOD = 4
EXCELLENT = 5

SCORE_CHOICES = (
    (LOW, 'Low'),
    (OK, 'Ok'),
    (NORMAL, 'Normal'),
    (GOOD, 'Good'),
    (EXCELLENT, 'Excellent'),
)


class User(AbstractUser):
	"""Custom User model"""
	phone_number = models.CharField(max_length=12, unique=True, blank=True, null=True)
	profile_pic = models.ImageField(
		upload_to="profile_pictures/",
		default="profile_pictures/no-photo-available-icon-20.jpg"
	)
	email = models.EmailField(unique=True)
	USERNAME_FIELD = 'email'
	REQUIRED_FIELDS = ['username',]


	def __str__(self):
		return self.username

	def get_full_name(self):
		return f'{self.first_name} {self.last_name}'
	
	def get_short_name(self):
		return f'{self.first_name}'


class CreditCard(models.Model):
	"""Credit Card model"""
	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='credit_cards')
	card_number = models.CharField(
		max_length=16, unique=True,
		blank=False, null=False
	)

	def __str__(self):
		return f'****{self.card_number[-4:]}'

	def save(self, *args, **kwargs):
		if CreditCard.objects.filter(user=self.user).count() < 5:
			return super(CreditCard, self).save(*args, **kwargs)
		else:
			raise ValidationError('The limit is 5 credit cards only.')


class Fandom(models.Model):
	"""Fandom model"""
	name = models.CharField(max_length=255, unique=True)
	fandom_type = models.CharField(max_length=30, choices=FANDOM_TYPE_CHOICES)

	def __str__(self):
		return self.name


class Character(models.Model):
	"""Character model"""
	name = models.CharField(max_length=50, unique=True)
	fandom = models.ForeignKey(Fandom, on_delete=models.CASCADE, related_name='characters')

	def __str__(self):
		return self.name


class Product(models.Model):
	"""Product model"""
	seller = models.ForeignKey(User, on_delete=models.CASCADE)
	title = models.CharField(max_length=255)
	description = models.TextField(max_length=1000)
	price = models.PositiveIntegerField()
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
	is_active = models.BooleanField()

	def __str__(self):
		return self.title

	def display_price(self):
		return f'{self.price} ₽'


class ProductImage(models.Model):
	"""Product Image model"""
	image = models.ImageField(
		upload_to="product_images/",
		default="product_images/No_image_available.svg.png"
	)
	product = models.ForeignKey(Product, on_delete=models.CASCADE)

	def __str__(self):
		return self.image

	def save(self, *args, **kwargs):
		if ProductImage.objects.filter(product=self.product).count() < 10:
			return super(ProductImage, self).save(*args, **kwargs)
		else:
			raise ValidationError('The limit is 10 images only.')


class Review(models.Model):
	"""Review model"""
	customer = models.ForeignKey(User, on_delete=models.CASCADE)
	product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
	score = models.IntegerField(choices=SCORE_CHOICES)
	text = models.TextField(max_length=1000)
	timestamp = models.DateTimeField(auto_now_add=True)
	edited = models.DateTimeField(auto_now=True)

	def __str__(self):
		return self.text


class Order(models.Model):
	"""Order model"""
	customer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
	name = models.CharField(max_length=100, null=True, blank=True)
	phone_number = models.CharField(max_length=12, blank=True, null=True)
	email = models.EmailField(blank=True, null=True)
	address = models.CharField(max_length=255, blank=False, null=False)
	timestamp = models.DateTimeField(auto_now_add=True)
	status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, blank=False, null=False)

	def clean(self):
		if not self.customer and not (self.name and self.phone_number):
			raise ValidationError('Either provide the field "customer" or fields "name", "phone_number" and "email".')

	def __str__(self):
		return self.customer.username

	def get_order_price(self):
		return sum(order_item.get_price() for order_item in self.order_items.all())


class OrderItem(models.Model):
	"""Order Product model"""
	product = models.ForeignKey(Product, on_delete=models.PROTECT)
	order = models.ForeignKey(
		Order, on_delete=models.CASCADE,
		related_name='order_items'
	)
	quantity = models.PositiveIntegerField(default=1)

	def __str__(self):
		return self.product.title

	def get_price(self):
		return self.quantity * self.product.price


class Favorite(models.Model):
	"""Favorite products model"""
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	product = models.ForeignKey(Product, on_delete=models.CASCADE)

	def __str__(self):
		return self.product

	def save(self, *args, **kwargs):
		if Favorite.objects.filter(user=self.user).count() < 100:
			return super(Favorite, self).save(*args, **kwargs)
		else:
			raise ValidationError('The limit is 100 favorite products only.')
