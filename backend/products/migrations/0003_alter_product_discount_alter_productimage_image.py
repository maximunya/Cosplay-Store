# Generated by Django 4.2.5 on 2024-02-07 20:08

from django.db import migrations, models
import products.models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0002_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='discount',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='productimage',
            name='image',
            field=models.ImageField(default='product_images/no-photo-available-icon-20.jpg', upload_to=products.models.ProductImage.get_upload_to),
        ),
    ]
