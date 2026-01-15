from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from .models import Booking


@shared_task
def send_payment_confirmation_email(booking_id: int):
    try:
        booking = Booking.objects.get(id=booking_id)
    except Booking.DoesNotExist:
        return False

    subject = "Booking confirmed"
    message = f"Your booking {booking.id} for {booking.listing.title} is confirmed.Thank you for your payment."
    recipient = booking.guest.email

    if not recipient:
        return False

    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL if hasattr(
        settings, 'DEFAULT_FROM_EMAIL') else None, [recipient], fail_silently=True)
    return True
