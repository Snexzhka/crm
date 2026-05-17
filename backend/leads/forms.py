from django import forms

from contracts.models import Contract
from .models import Lead

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Lead
        fields = ["first_name", "last_name", "phone", "email", "advert_name"]


class ConvertLeadForm(forms.Form):
    contract = forms.ModelChoiceField(queryset=Contract.objects.none(), label="Контракт")

    def __init__(self, *args, **kwargs):
        lead = kwargs.pop('lead')
        super().__init__(*args, **kwargs)
        self.fields['contract'].queryset = lead.contract_set.all()