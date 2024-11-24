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
            inventory_to_stock=50,
            warranty_status="Active",
            distributor_info="Distributor XYZ",
            description="High-quality sports shoes",
            category="Footwear",
            base_price=100.00,
            price=90.00,
            discount=self.discount,
            popularity_score=4.5,
            avg_rating=4.2,
        )

    def test_add_session_to_request(self):
        client = Client()
        request = client.get("/")
        middleware = SessionMiddleware(lambda request: None)  # No-op function
        middleware.process_request(request)
        request.session.save()
        self.assertIsNotNone(request.session.session_key, "Session should have a session key.")

    def test_get_or_create_guest_with_cart(self):
        client = Client()
        client.get("/")  # Trigger session creation
        session_key = client.session.session_key
        self.assertIsNotNone(session_key, "Session key should not be None")

        # Manually create a guest
        guest = Guest.objects.create(session_id=session_key)

        # Create a cart
        guest_content_type = ContentType.objects.get_for_model(Guest)
        cart = ShoppingCart.objects.create(owner_content_type=guest_content_type, owner_object_id=guest.pk)
        self.assertIsNotNone(cart, "ShoppingCart should be created.")

    def test_home_view(self):
        client = Client()
        response = client.get("/")  # Home URL
        self.assertEqual(response.status_code, 200, "Home view should return a 200 OK response.")
        self.assertTemplateUsed(response, "home.html", "Home view should use the 'home.html' template.")
