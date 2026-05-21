from django.db import models




class Customer(models.Model):
    lead = models.ForeignKey("leads.Lead", on_delete=models.DO_NOTHING, related_name="customers")
    contract = models.ForeignKey("contracts.Contract", on_delete=models.SET_DEFAULT, default="", related_name="customers")

    def get_profile(self):
        from contracts.models import Contract
        from leads.models import Lead

        profiles = Lead.objects.filter(profile=self)
        contracts = Contract.objects.filter(contract=self)
        return [{"name":p.first_name, "lastname": p.last_name if p.last_name else "",
                 "phone":p.phone, "email":p.email}
            for p in profiles
        ], [{"date":contract.start_date+contract.duration}
            for contract in contracts]


    def __str__(self):
        return f"{self.lead.first_name} {self.lead.last_name}-{self.contract.name}{self.contract.start_date}"
