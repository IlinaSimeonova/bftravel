"""
Example background tasks for Django-Q2.

Usage:
    from django_q.tasks import async_task, schedule
    from bftravel.tasks import send_welcome_email, process_booking

    # Run task asynchronously
    async_task('bftravel.tasks.send_welcome_email', user_id=123)

    # Run with options
    async_task(
        'bftravel.tasks.process_booking',
        booking_id=456,
        timeout=120,
        hook='bftravel.tasks.booking_complete_hook'
    )
"""

import logging

logger = logging.getLogger(__name__)


def send_welcome_email(user_id):
    """Send welcome email to a new user."""
    # Example: Replace with actual email logic
    logger.info(f"Sending welcome email to user {user_id}")
    # from django.core.mail import send_mail
    # user = User.objects.get(id=user_id)
    # send_mail(subject, message, from_email, [user.email])
    return f"Email sent to user {user_id}"


def process_booking(booking_id):
    """Process a booking asynchronously."""
    logger.info(f"Processing booking {booking_id}")
    # Add your booking processing logic here
    return f"Booking {booking_id} processed"


def booking_complete_hook(task):
    """Hook called after a task completes."""
    logger.info(f"Task {task.name} completed with result: {task.result}")
