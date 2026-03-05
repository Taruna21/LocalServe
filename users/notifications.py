from .models import Notification

def notify(recipient, notif_type, title, message):
    """Create a notification for a user."""
    Notification.objects.create(
        recipient  = recipient,
        notif_type = notif_type,
        title      = title,
        message    = message,
    )


def notify_new_application(job, application):
    """Tell recruiter someone applied to their job."""
    notify(
        recipient  = job.posted_by,
        notif_type = 'application',
        title      = f'New application for "{job.title}"',
        message    = f'{application.applicant_name} ({application.applicant_phone}) applied to your job in {job.city}.',
    )


def notify_status_update(application):
    """Tell seeker their application status changed."""
    notify(
        recipient  = application.applicant,
        notif_type = 'status_update',
        title      = f'Application update — {application.job.title}',
        message    = f'Your application status has been updated to: {application.status.upper()}.',
    )
