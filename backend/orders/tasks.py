from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model

from twilio.rest import Client
from backend.celery import app
from .models import Order


User = get_user_model()

def send_sms(message_body, to_phone_number):
    # Отправка SMS
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    
    message = client.messages.create(
        body=message_body,
        from_=settings.TWILIO_PHONE_NUMBER,
        to=to_phone_number
    )
    
    return message


def send_email(subject, email_body, recipient_email):
    # Отправка email
    email_message = send_mail(
        subject,
        email_body,
        settings.EMAIL_HOST_USER,
        [recipient_email],
        fail_silently=False,
    )
    
    return email_message


@app.task
def send_order_created_notifications(user_is_authenticated, order_id):
    order = Order.objects.get(id=order_id)

    if user_is_authenticated:
        recipient_name = order.customer.first_name
        recipient_email = order.customer.email
        to_phone_number = order.customer.phone_number
        link = f'http://localhost:8000/api/orders/{order.slug}'
    else:
        recipient_name = order.name
        recipient_email = order.email
        to_phone_number = order.phone_number
        link = f'http://localhost:8000/api/orders/{order.slug}/'

    # SMS уведомление
    sms_message_body = f'{recipient_name}, Ваш заказ №{order.slug} успешно оформлен и ожидает оплаты. ' \
                       f'Оплатить заказ можно по ссылке: {link}' 
    send_sms(sms_message_body, to_phone_number)

    # Email уведомление
    email_subject = 'Новый заказ'
    email_body = f'{recipient_name}, Ваш заказ №{order.slug} успешно оформлен и ожидает оплаты. ' \
                 f'Оплатить заказ можно по ссылке: {link}' 
    send_email(email_subject, email_body, recipient_email)


@app.task
def send_order_paid_notifications(user_is_authenticated, order_id):
    order = Order.objects.get(id=order_id)

    if user_is_authenticated:
        recipient_name = order.customer.first_name
        recipient_email = order.customer.email
        to_phone_number = order.customer.phone_number
        link = f'http://localhost:8000/api/orders/{order.slug}'
    else:
        recipient_name = order.name
        recipient_email = order.email
        to_phone_number = order.phone_number
        link = f'http://localhost:8000/api/orders/{order.slug}/'

    # SMS уведомление
    sms_message_body = f'{recipient_name}, Ваш заказ №{order.slug} успешно оплачен. ' \
                       f'Подробнее о заказе по ссылке: {link}' 
    send_sms(sms_message_body, to_phone_number)

    # Email уведомление
    email_subject = f'Заказ №{order.slug} оплачен'
    email_body = f'{recipient_name}, Ваш заказ №{order.slug} успешно оплачен. ' \
                 f'Подробнее о заказе по ссылке: {link}' 
    send_email(email_subject, email_body, recipient_email)