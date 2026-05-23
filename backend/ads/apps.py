"""
Конфигурация для приложения ads
"""

from django.apps import AppConfig


class AdsConfig(AppConfig):
    """

    Конфигурация для приложения 'ads'.

    Атрибуты:
        default_auto_field: тип автоинкрементного поля (устанавливается
        в 'django.db.models.BigAutoField').
        name: имя приложения (путь к пакету).
        verbose_name: отображаемое имя в админке (на русском).
    """

    name = "ads"
    verbose_name = "Рекламные компании"
