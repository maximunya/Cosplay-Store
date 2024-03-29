# Generated by Django 4.2.5 on 2024-02-28 22:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0003_alter_product_discount_alter_productimage_image'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='answer',
            options={'ordering': ['timestamp']},
        ),
        migrations.AlterModelOptions(
            name='productimage',
            options={'ordering': ['id']},
        ),
        migrations.AlterModelOptions(
            name='review',
            options={'ordering': ['-timestamp']},
        ),
        migrations.AlterField(
            model_name='product',
            name='slug',
            field=models.SlugField(allow_unicode=True, blank=True, editable=False, max_length=255, unique=True),
        ),
    ]
