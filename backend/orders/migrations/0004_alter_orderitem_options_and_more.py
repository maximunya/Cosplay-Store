# Generated by Django 4.2.5 on 2024-02-18 16:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0003_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='orderitem',
            options={'ordering': ['status', '-created_at']},
        ),
        migrations.RenameField(
            model_name='order',
            old_name='timestamp',
            new_name='created_at',
        ),
        migrations.RenameField(
            model_name='orderitem',
            old_name='timestamp',
            new_name='created_at',
        ),
        migrations.AddField(
            model_name='order',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='orderitem',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
