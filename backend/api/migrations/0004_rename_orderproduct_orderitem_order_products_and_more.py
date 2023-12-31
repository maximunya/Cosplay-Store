# Generated by Django 4.2 on 2023-08-04 22:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_alter_user_phone_number'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='OrderProduct',
            new_name='OrderItem',
        ),
        migrations.AddField(
            model_name='order',
            name='products',
            field=models.ManyToManyField(through='api.OrderItem', to='api.product'),
        ),
        migrations.AlterField(
            model_name='product',
            name='cosplay_character',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='products', to='api.character'),
        ),
    ]
