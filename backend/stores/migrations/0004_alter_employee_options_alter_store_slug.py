# Generated by Django 4.2.5 on 2024-02-28 22:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stores', '0003_alter_store_check_number_alter_store_name_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='employee',
            options={'ordering': ['-is_owner', '-is_admin', 'hired_at']},
        ),
        migrations.AlterField(
            model_name='store',
            name='slug',
            field=models.SlugField(blank=True, max_length=255, unique=True),
        ),
    ]