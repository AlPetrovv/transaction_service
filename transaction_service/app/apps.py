from django.apps import AppConfig


class ReportsConfig(AppConfig):
    name = "app"
    verbose_name = "Transfers"

    def ready(self):
        import app.signals
