from django.db import models
from django.core.validators import MinLengthValidator
from django.utils.text import slugify

from users.models import User


class Store(models.Model):
	'''Store model'''
	ORGANIZATION_TYPE_CHOICES = (
		('IE', 'Individual Entrepreneur'),
		('LLC', 'LLC'),
		('JSC', 'JCS'),
		('SE', 'Self-Employed'),
	)

	def get_upload_to(instance, filename):
		store_id = instance.id
		return f"store_logos/store_{store_id}/{filename}"

	slug = models.SlugField(unique=True, max_length=255, blank=True)
	owner = models.OneToOneField(User, on_delete=models.CASCADE, related_name='store')
	organization_type = models.CharField(max_length=50, choices=ORGANIZATION_TYPE_CHOICES)
	organization_name = models.CharField(max_length=255)
	name = models.CharField(max_length=50, unique=True)
	taxpayer_number = models.CharField(max_length=10, validators=[MinLengthValidator(10, 'Incorrect ITN format.')], unique=True)
	check_number = models.CharField(max_length=20, validators=[MinLengthValidator(20, 'Incorrect check format.')], unique=True)
	balance = models.PositiveIntegerField(default=0)
	is_verified = models.BooleanField(default=False)
	is_admin_store = models.BooleanField(default=False)
	logo = models.ImageField(
		upload_to=get_upload_to,
		default="store_logos/no-photo-available-icon-20.jpg",
		null=False,
		blank=False
	)
	bio = models.TextField(max_length=300, blank=True, null=True)
	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.name
	
	def save(self, *args, **kwargs):
		if not self.slug:
			self.slug = slugify(self.name, allow_unicode=True)
		return super().save(*args, **kwargs)
	

class Employee(models.Model):
	'''Employee Model'''
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='employees')
	is_owner = models.BooleanField(default=False)
	is_admin = models.BooleanField(default=False)
	hired_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f'{self.store.name} - {self.user.username}'
	
	class Meta:
		unique_together = ('user', 'store')
		ordering = ['-is_owner', '-is_admin', 'hired_at']