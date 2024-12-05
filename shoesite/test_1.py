from django.test import TestCase, Client
from django.contrib.contenttypes.models import ContentType
from django.contrib.sessions.middleware import SessionMiddleware
from .models import Discount, Product, Guest, ShoppingCart
from datetime import date

class GuestCartTestCase(TestCase):
    def setUp(self):
        # Create a sample discount
        self.discount = Discount.objects.create(
            discount_name="Black Friday Sale",
            discount_rate=20.00,
            start_date=date(2024, 11, 20),
            end_date=date(2024, 11, 30),
        )
        # Create a sample product
        self.product = Product.objects.create(
            model="Shoe Model X",
            serial_number="123456",
            stock=100,
            warranty_status="Active",
            distributor_info="Distributor XYZ",
            description="High-quality sports shoes",
            category="Footwear",
            base_price=100.00,
            price=90.00,
            discount=None,  # Discount is null
            popularity_score=4.5,
            avg_rating=4.2,
        )






