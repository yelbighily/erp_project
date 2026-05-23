from django.apps import AppConfig


class ErpCoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.erp_core"
    label = "erp_core"

    def ready(self):
        import apps.erp_core.signals  # noqa — registers signal handlers
        