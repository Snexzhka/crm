import datetime
import os
import shutil
from datetime import timedelta

from django.contrib.contenttypes.models import ContentType
from django.test import TestCase, Client
from django.contrib.auth.models import User, Permission
from django.urls import reverse
from django.conf import settings
from django.utils import timezone

from .models import Contract
from ads.models import Advert
from leads.models import Lead
from products.models import Product


class ContractModelTest(TestCase):
    def test_model_contract(self):
        self.product = Product.objects.create(
            name="TestProduct",
            cost=100,
            description="qwerty",
        )
        self.ads = Advert.objects.create(
            name="TestAdvert",
            products=self.product,
            promotion_path="news",
            budget=77,
        )
        self.lead = Lead.objects.create(
            first_name="Test",
            last_name="Testovich",
            phone="+1234567",
            email="test@test.ru",
            advert_name=self.ads,
        )
        self.contract = Contract.objects.create(
            name="TestContract",
            products=self.product,
            duration=timedelta(days=5),
            cost=120,
            lead=self.lead,
        )

        self.assertEqual(self.contract.name, "TestContract")
        self.assertNotEqual(self.contract.cost, 1100)
        self.assertEqual(self.contract.products.name, "TestProduct")
        self.assertEqual(str(self.contract.start_date), str(datetime.datetime.now().date()))
        self.assertEqual(Contract.objects.count(), 1)
        self.assertEqual(self.contract.lead.phone, "+1234567")