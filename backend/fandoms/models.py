from django.db import models
from django.utils.text import slugify


FANDOM_TYPE_CHOICES = (
	('Games', 'Games'),
	('Anime', 'Anime'),
	('Series', 'Series'),
	('Movies', 'Movies'),
	('Cartoons', 'Cartoons'),
	('Other', 'Other'),
)


class Fandom(models.Model):
	"""Fandom model"""
	def get_upload_to(instance, filename):
		return f"fandom_images/{instance.slug}/{filename}"

	slug = models.SlugField(unique=True, max_length=255, blank=True)
	name = models.CharField(max_length=255, unique=True)
	fandom_type = models.CharField(max_length=10, choices=FANDOM_TYPE_CHOICES)
	image = models.ImageField(
		upload_to=get_upload_to,
		default="fandom_images/no-photo-available-icon-20.jpg"
	)

	def __str__(self):
		return self.name
	
	def save(self, *args, **kwargs):
		if not self.slug:
			self.slug = slugify(self.name, allow_unicode=True)
		return super().save(*args, **kwargs)
	
	class Meta:
		ordering = ['name']
	

class Character(models.Model):
	"""Character model"""
	def get_upload_to(instance, filename):
		return f"character_images/{instance.fandom.slug}/{instance.slug}/{filename}"
	
	slug = models.SlugField(unique=True, max_length=255, blank=True)
	name = models.CharField(max_length=255, unique=True)
	fandom = models.ForeignKey(Fandom, on_delete=models.CASCADE, related_name='characters')
	image = models.ImageField(
		upload_to=get_upload_to,
		default="character_images/no-photo-available-icon-20.jpg"
	)

	def __str__(self):
		return self.name
	
	def save(self, *args, **kwargs):
		if not self.slug:
			self.slug = slugify(self.name, allow_unicode=True)
		return super().save(*args, **kwargs)
	
	class Meta:
		ordering = ['name']


