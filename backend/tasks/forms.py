"""
Форма для создания и обновления объектов модели
"""
from django import forms

from .models import Task

class TaskForm(forms.ModelForm):
    """
    Определены необходимые поля формы
    """
    class Meta:
        model = Task
        fields = ["title", "user", "description", "is_completed", "due_date"]
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date'}),

        }
