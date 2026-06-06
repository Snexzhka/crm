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

        widgets = {
            "duration": forms.TextInput(attrs={
                "placeholder": "Пример: 5 days, 1 day 12 hours, 2 weeks"
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["file"].required = False
