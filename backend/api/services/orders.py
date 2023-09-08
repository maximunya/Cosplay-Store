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

def send_order_success_notifications(request, order):
    if request.user.is_authenticated:
        recipient_name = order.customer.first_name
        recipient_email = order.customer.email
        to_phone_number = order.customer.phone_number
        link = 'http://localhost:8000/api/orders/'
    else:
        recipient_name = order.name
        recipient_email = order.email
        to_phone_number = order.phone_number
        link = f'http://localhost:8000/api/order/{order.id}/'

    # SMS уведомление
    sms_message_body = f'{recipient_name}, Ваш заказ №{order.id} успешно оформлен. ' \
                       f'Подробную информацию о заказе можете узнать по ссылке: {link}' 
    send_sms(sms_message_body, to_phone_number)

    # Email уведомление
    email_subject = 'Новый заказ'
    email_body = f'{recipient_name}, Ваш заказ №{order.id} успешно оформлен. ' \
                 f'Подробную информацию о заказе можете узнать по ссылке: {link}' 
    send_email(email_subject, email_body, recipient_email)
