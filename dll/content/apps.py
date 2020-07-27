from django.apps import AppConfig


class ContentConfig(AppConfig):
    name = "dll.content"

    def ready(self):
        import dll.content.signals
