"""
Celery tasks for the listings app.
Handles background tasks like sending booking confirmation emails.
"""

from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from .models import Booking


@shared_task(bind=True, max_retries=3)
def send_booking_confirmation_email(self, booking_id: int):
    """
    Send booking confirmation email to the guest asynchronously.

    Args:
        booking_id (int): The ID of the booking to send confirmation for.

    Returns:
        bool: True if email was sent successfully, False otherwise.
    """
    try:
        booking = Booking.objects.get(id=booking_id)
    except Booking.DoesNotExist:
        return False

    subject = "Booking Confirmation"
    recipient = booking.guest.email

    if not recipient:
        return False

    # Prepare email context
    context = {
        'guest_name': booking.guest.first_name or booking.guest.username,
        'listing_title': booking.listing.title,
        'booking_id': booking.id,
        'check_in': booking.check_in,
        'check_out': booking.check_out,
        'total_price': booking.total_price,
        'listing_url': f"{settings.SITE_URL}/listings/{booking.listing.id}/"
    }

    # Try to render HTML email template, fall back to plain text
    try:
        html_message = render_to_string('booking_confirmation.html', context)
    except Exception:
        html_message = None

    # Plain text message fallback
    message = f"""
Dear {context['guest_name']},

Your booking for {context['listing_title']} has been confirmed!

Booking Details:
- Booking ID: {context['booking_id']}
- Check-in: {context['check_in']}
- Check-out: {context['check_out']}
- Total Price: ${context['total_price']}

Thank you for using ALX Travel App!

Best regards,
ALX Travel App Team
    """.strip()

    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [recipient],
            html_message=html_message,
            fail_silently=False
        )
        return True
    except Exception as exc:
        # Retry the task if email sending fails
        raise self.retry(exc=exc, countdown=60)  # Retry after 60 seconds


@shared_task(bind=True, max_retries=3)
def send_payment_confirmation_email(self, booking_id: int):
    """
    Send payment confirmation email to the guest asynchronously.
    This task is triggered when a payment is successfully completed.

    Args:
        booking_id (int): The ID of the booking with completed payment.

    Returns:
        bool: True if email was sent successfully, False otherwise.
    """
    try:
        booking = Booking.objects.get(id=booking_id)
    except Booking.DoesNotExist:
        return False

    subject = "Payment Confirmed - Your Booking is Confirmed"
    recipient = booking.guest.email

    if not recipient:
        return False

    # Prepare email context
    context = {
        'guest_name': booking.guest.first_name or booking.guest.username,
        'listing_title': booking.listing.title,
        'booking_id': booking.id,
        'total_price': booking.total_price,
        'listing_url': f"{settings.SITE_URL}/listings/{booking.listing.id}/"
    }

    # Try to render HTML email template, fall back to plain text
    try:
        html_message = render_to_string('payment_confirmation.html', context)
    except Exception:
        html_message = None

    # Plain text message fallback
    message = f"""
Dear {context['guest_name']},

Your payment of ${context['total_price']} for {context['listing_title']} has been processed successfully!

Booking ID: {context['booking_id']}

Your booking is now confirmed. Check your email for further details and instructions.

Thank you for your payment!

Best regards,
ALX Travel App Team
    """.strip()

    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [recipient],
            html_message=html_message,
            fail_silently=False
        )
        return True
    except Exception as exc:
        # Retry the task if email sending fails
        raise self.retry(exc=exc, countdown=60)  # Retry after 60 seconds
