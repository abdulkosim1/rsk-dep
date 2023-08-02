from django.conf import settings
from main.celery import app

@app.task
def send_sms_code(phone,code,body):
    from twilio.rest import Client
    client = Client(settings.TWILIO_SID, settings.TWILIO_AUTH_TOKEN)
    message = client.messages.create(
        body=f'Это Ваш активационный код {code}',
        from_=settings.TWILIO_NUMBER,
        to=phone
    )
