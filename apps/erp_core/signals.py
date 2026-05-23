# Automatically clears the cache whenever someone enables or disables a module

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import CompanyModule
from .module_utils import invalidate_module_cache


@receiver(post_save, sender=CompanyModule)
def on_company_module_save(sender, instance, **kwargs):
    invalidate_module_cache(instance.company_id)


@receiver(post_delete, sender=CompanyModule)
def on_company_module_delete(sender, instance, **kwargs):
    invalidate_module_cache(instance.company_id)