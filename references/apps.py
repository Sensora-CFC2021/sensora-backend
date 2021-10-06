from django.apps import AppConfig


class ReferencesConfig(AppConfig):
    name = 'references'

    def ready(self):
        import references.signals