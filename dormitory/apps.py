from django.apps import AppConfig


class DormitoryConfig(AppConfig):
    default_auto_field = 'django.db.models.AutoField'
    name = 'dormitory'

    def ready(self):
        import dormitory.signals
