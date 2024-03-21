import uuid
from datetime import datetime

from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
	"""Custom User model"""
	def get_upload_to(instance, filename):
		user_id = instance.id
		return f"profile_pictures/user_{user_id}/{filename}"
	
	phone_number = models.CharField(max_length=12, unique=True, blank=True, null=True)
	email = models.EmailField(unique=True)
	birth_date = models.DateField(null=True, blank=True)
	profile_pic = models.ImageField(
		upload_to=get_upload_to,
		default="profile_pictures/no-photo-available-icon-20.jpg"
	)
	USERNAME_FIELD = 'email'
	REQUIRED_FIELDS = ['username']

	def __str__(self):
		return self.username

	def get_age(self):
		if self.birth_date:
			today = datetime.today()
			age = today.year - self.birth_date.year - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))
			return age
		else:
			return None
		
	class Meta:
		ordering = ['username']
	

class Address(models.Model):
	"""Address model"""
	uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
	name = models.CharField(max_length=255, blank=True)
	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses', blank=True, null=True)
	address = models.CharField(max_length=255, blank=False, null=False)
	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f'{self.name} - {self.address}'

	def save(self, *args, **kwargs):
		if self.user:
			if Address.objects.filter(user=self.user).count() < 5:
				return super(Address, self).save(*args, **kwargs)
			else:
				raise ValidationError('The limit is 5 addresses only.')
		return super(Address, self).save(*args, **kwargs)
	
	class Meta:
		ordering = ['created_at']
