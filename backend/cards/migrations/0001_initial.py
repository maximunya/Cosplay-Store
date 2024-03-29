# Generated by Django 4.2.5 on 2024-02-02 21:23

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Card',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('card_number', models.CharField(max_length=16)),
                ('balance', models.PositiveIntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('transaction_type', models.CharField(choices=[('Deposit', 'Deposit'), ('Purchase', 'Purchase'), ('Sale', 'Sale'), ('Comission', 'Comission')], max_length=10)),
                ('amount', models.PositiveIntegerField()),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(default='Success')),
                ('card', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='card_transactions', to='cards.card')),
            ],
        ),
    ]
