from django.apps import AppConfig


class TransfersAppConfig(AppConfig):
    name = "app"
    verbose_name = "Transfers"

    def ready(self):
        from . import signals  # noqa: F401
