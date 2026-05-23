"""
Формы для вывода данных
"""

from django import forms

from .models import Contract


class ContractForm(forms.ModelForm):
    """
    Форма для вывода данных по контрактам, определяет поля
    и переопределяет их значение при выводе (по необходимости)
    """

    class Meta:
        model = Contract
        fields = "name", "products", "duration", "file", "cost", "lead"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["file"].required = False
