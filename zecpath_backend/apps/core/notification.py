from .models import NotificationLog

def send_application_notification(email, subject, message):

    print("Notification function called!")

    NotificationLog.objects.create(
        email=email,
        subject=subject,
        message=message,
        status="sent"
    )

    return True