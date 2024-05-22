
from django.core.mail import send_mail
from django.conf import settings

def send_email_gmail(subject, to_emails, html_content):
    HOST_USER = settings.EMAIL_HOST_USER

    RECIPIENT_LIST = [to_emails]
    
    try:
        response = send_mail(subject,html_content,HOST_USER,RECIPIENT_LIST,fail_silently=False)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print(e)