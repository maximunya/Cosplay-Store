# Generated by Django 4.2.5 on 2024-02-28 22:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_alter_address_user'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='address',
            options={'ordering': ['created_at']},
        ),
        migrations.AlterModelOptions(
            name='user',
            options={'ordering': ['username']},
        ),
    ]
