"""
Форма для создания и обновления модели услуг
"""
from django import forms

from .models import Product


class ProductForm(forms.ModelForm):
    """
    Определены используемые поля формы
    """
    class Meta:
        model = Product
        fields = ["name", "description", "cost"]
