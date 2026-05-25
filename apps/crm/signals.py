from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Lead


@receiver(post_save, sender=Lead)
def on_lead_status_change(sender, instance, created, **kwargs):
    """
    Placeholder for future automation:
    - Send welcome email on new lead
    - Notify assigned user
    - Trigger scoring update
    """
    pass