"""
Формы для создания и вывода объекта рекламной услуги
"""
from django import forms

from .models import Advert

class AdvertForm(forms.ModelForm):
    """
    Класс вывода формы для рекламной услуги
    """
    class Meta:
        """
        Класс установки полей вывода и используемой модели
        """
        model = Advert
        fields = "name", "budget", "promotion_path", "products"
