from django.apps import AppConfig
from django.utils.module_loading import autodiscover_modules


class StarkConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'stark'

    def ready(self):
        """ready.
        项目加载前自动加载各app下的`stark`模块
        :param self:
        """
        autodiscover_modules('stark')

