"""
Формы для приложения 'customers'.

Содержит форму для отображения полей
"""
from django import forms

from .models import Customer

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = "lead", "contract"
