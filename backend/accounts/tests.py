from django.test import TestCase
import pytest, pytest_django

@pytest.mark.django_db
def test_product_create(product):
    assert product.name == "TestProd"
