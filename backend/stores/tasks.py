from django.core.mail import send_mail
from django.conf import settings

from backend.celery import app
from twilio.rest import Client
from orders.models import OrderItem, Order, ORDER_ITEM_STATUS_CHOICES


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
def send_order_item_sent_notifications(order_item_id):
    order_item = OrderItem.objects.select_related('order', 'product').get(pk=order_item_id)

    recipient_name = order_item.order.name
    recipient_email = order_item.order.email
    to_phone_number = order_item.order.phone_number
    link = f'http://localhost:8000/api/orders/items/{order_item.slug}'

    # SMS уведомление
    sms_message_body = f'{recipient_name}, товар "{order_item.product.title}" отправлен продавцом. ' \
                       f'Подробнее о заказе по ссылке: {link}' 
    send_sms(sms_message_body, to_phone_number)

    # Email уведомление
    email_subject = f'Товар отправлен'
    email_body = f'{recipient_name}, товар "{order_item.product.title}" отправлен продавцом. ' \
                 f'Подробнее о заказе по ссылке: {link}' 
    send_email(email_subject, email_body, recipient_email)


@app.task
def send_order_item_received_notifications(order_item_id):
    order_item = OrderItem.objects.select_related('order', 'product').get(pk=order_item_id)

    recipient_name = order_item.order.name
    recipient_email = order_item.order.email
    to_phone_number = order_item.order.phone_number
    link = f'http://localhost:8000/api/products/{order_item.product.id}/reviews/create/'

    # SMS уведомление
    sms_message_body = f'{recipient_name}, поделитесь своими впечатлениями о товаре по ссылке: {link}'
    send_sms(sms_message_body, to_phone_number)

    # Email уведомление
    email_subject = f'Оставьте отзыв о товаре'
    email_body = f'{recipient_name}, поделитесь своими впечатлениями о товаре по ссылке: {link}'
    send_email(email_subject, email_body, recipient_email)


@app.task
def send_order_item_cancelled_notifications(order_item_id):
    order_item = OrderItem.objects.select_related('order', 'product').get(pk=order_item_id)

    recipient_name = order_item.order.name
    recipient_email = order_item.order.email
    to_phone_number = order_item.order.phone_number
    link = f'http://localhost:8000/api/orders/items/{order_item.slug}'

    # SMS уведомление
    sms_message_body = f'{recipient_name}, Ваш заказ "{order_item.product.title}" был отменён. ' \
                       f'Подробнее о причинах и возврате средств по ссылке: {link}' 
    send_sms(sms_message_body, to_phone_number)

    # Email уведомление
    email_subject = f'Заказ отменён'
    email_body = f'{recipient_name}, Ваш заказ "{order_item.product.title}" был отменён. ' \
                 f'Подробнее о причинах и возврате средств по ссылке: {link}' 
    send_email(email_subject, email_body, recipient_email)


@app.task
def update_full_order_status(order_id):
    order = Order.objects.prefetch_related('order_items').get(pk=order_id)
    order_item_statuses = list(order.order_items.values_list('status', flat=True))
    status_counts = {status: order_item_statuses.count(str(status)) for status, _ in ORDER_ITEM_STATUS_CHOICES}

    if status_counts[0] == len(order_item_statuses):
        order.status = 0
    elif status_counts[1] > 0:
        order.status = 1
    elif status_counts[2] > 0:
        order.status = 2
    elif status_counts[3] > 0:
        order.status = 3
    elif status_counts[4] == (len(order_item_statuses) - status_counts[0]):
        order.status = 4

    order.save()