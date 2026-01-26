from django.apps import AppConfig


class EkbangConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ekbang'

def ready(self):
        import ekbang.signals