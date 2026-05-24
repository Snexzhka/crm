"""
Модель для приложения активных клиентов
"""

from django.db import models

from contracts.models import Contract
from leads.models import Lead


class Customer(models.Model):
    """
    Модель для активных клиентов.
    Использует связи с приложениями потенциальных клиентов
    и контрактов.
    Поля:
        lead:связь с активным клиентом
        contract:связь с контрактом

    """

    lead: models.ForeignKey["Lead"] = models.ForeignKey(
        "leads.Lead",
        on_delete=models.PROTECT,
        related_name="customers",
    )
    contract: models.ForeignKey["Contract"] = models.ForeignKey(
        "contracts.Contract",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="customers",
    )

    def get_profile(self):
        profiles = Lead.objects.filter(profile=self)
        contracts = Contract.objects.filter(contract=self)
        return [
            {
                "name": p.first_name,
                "lastname": p.last_name if p.last_name else "",
                "phone": p.phone,
                "email": p.email,
            }
            for p in profiles
        ], [{"date": contract.start_date + contract.duration} for contract in contracts]

    def __str__(self):
        lead_name = self.lead.first_name if self.lead else "Без лида"
        contract_name = self.contract.name if self.contract else "Без контракта"
        return f"{lead_name} - {contract_name}"
