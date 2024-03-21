from django.core.mail import send_mail
from twilio.rest import Client
from django.conf import settings


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


def send_order_created_notifications(user, order):
    if user.is_authenticated:
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


def send_order_paid_notifications(user, order):
    if user.is_authenticated:
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


def send_order_item_sent_notifications(customer, order_item):
    if customer:
        recipient_name = customer.first_name
        recipient_email = customer.email
        to_phone_number = customer.phone_number
        link = f'http://localhost:8000/api/orders/items/{order_item.slug}'
    else:
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


def send_order_item_received_notifications(customer, order_item):
    if customer:
        recipient_name = customer.first_name
        recipient_email = customer.email
        to_phone_number = customer.phone_number
        link = f'http://localhost:8000/api/products/{order_item.product.id}/reviews/create/'
    else:
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


def send_order_item_cancelled_notifications(customer, order_item):
    if customer:
        recipient_name = customer.first_name
        recipient_email = customer.email
        to_phone_number = customer.phone_number
        link = f'http://localhost:8000/api/orders/items/{order_item.slug}'
    else:
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