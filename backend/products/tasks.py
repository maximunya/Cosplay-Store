from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model
from django.template.loader import render_to_string

from backend.celery import app
from .models import Product

User = get_user_model()

@app.task
def send_async_email(subject, message, recipient_list):
    send_mail(subject, message, settings.EMAIL_HOST_USER, recipient_list, html_message=message, fail_silently=True)

@app.task
def send_daily_offer_email():
    subject = 'Daily cosplay offer!'
    users = User.objects.filter(is_active=True).only('email', 'username', 'first_name').order_by('?')

    for user in users:
        products = Product.objects.only('slug', 'title', 'price').filter(is_active=True).order_by('?')[:5]
        context = {
            'user': user,
            'products': products,
        }
        message = render_to_string('email_template.html', context)
        
        send_async_email.delay(subject, message, [user.email])