from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from .models import Customer, Product, ShoppingCart, CartItem, Wishlist, Comment, Rating, OrderItem, Order, Discount, Category, WishlistItem, Refund
from django.contrib.contenttypes.models import ContentType
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta

class RefundTests(TestCase):

    def setUp(self):
        # Create a category for the product
        self.category = Category.objects.create(name="Footwear")
        
        # Create a customer
        self.customer = Customer.objects.create(name="John Doe", email="johndoe@example.com", balance=100.00)
        
        # Create a product that belongs to the category
        self.product = Product.objects.create(
            model="Running Shoes",
            serial_number="SN001",
            cost=30.00,
            price=50.00,
            stock=10,
            description="Comfortable running shoes",
            category=self.category
        )
        
        # Create an order
        self.order = Order.objects.create(
            order_date=timezone.now() - timedelta(days=5),
            status="Delivered",
            total_amount=150.00,
            discount_applied=False,
            customer=self.customer
        )

        # Create an order item
        self.order_item = OrderItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=2,
            price_per_item=50.00
        )
    
    def test_request_refund_success(self):
        # Test refund request within 30 days
        url = reverse('request_refund', args=[self.order_item.pk])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 201)
        self.assertIn("refund_id", response.json())
        self.assertEqual(response.json()["status"], "success")
    
    def test_request_refund_non_delivered_order(self):
        # Update order status to non-delivered
        self.order.status = "Processing"
        self.order.save()
        
        url = reverse('request_refund', args=[self.order_item.pk])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["status"], "error")
        self.assertEqual(response.json()["message"], "Refund can only be requested for delivered orders.")
    
    def test_request_refund_after_30_days(self):
        # Update order date to more than 30 days ago
        self.order.order_date = timezone.now() - timedelta(days=40)
        self.order.save()
        
        url = reverse('request_refund', args=[self.order_item.pk])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["status"], "error")
        self.assertEqual(response.json()["message"], "Refund request is past the 30-day period.")
    
    def test_request_refund_multiple_times(self):
        # Submit a refund request
        url = reverse('request_refund', args=[self.order_item.pk])
        self.client.post(url)

        # Try to submit a refund again for the same order item
        response = self.client.post(url)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["status"], "error")
        self.assertEqual(response.json()["message"], "Refund request already exists for this order item.")
    
    def test_approve_refund_success(self):
        # Submit a refund request
        url = reverse('request_refund', args=[self.order_item.pk])
        response = self.client.post(url)
        refund_id = response.json()["refund_id"]

        # Approve the refund
        approve_url = reverse('approve_refund', args=[refund_id])
        response = self.client.post(approve_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "success")
        self.assertEqual(response.json()["message"], "Refund approved successfully.")
    
    def test_disapprove_refund_success(self):
        # Submit a refund request
        url = reverse('request_refund', args=[self.order_item.pk])
        response = self.client.post(url)
        refund_id = response.json()["refund_id"]

        # Disapprove the refund
        disapprove_url = reverse('disapprove_refund', args=[refund_id])
        response = self.client.post(disapprove_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "success")
        self.assertEqual(response.json()["message"], "Refund request disapproved successfully.")
    
    def test_get_pending_refunds(self):
        # Create another refund for testing
        url = reverse('request_refund', args=[self.order_item.pk])
        response = self.client.post(url)
        refund_id = response.json()["refund_id"]

        # Fetch pending refunds
        url = reverse('get_pending_refunds')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("pending_refunds", response.json())
        self.assertEqual(len(response.json()["pending_refunds"]), 1)

    def test_check_order_item_refunded(self):
        # Submit a refund request
        url = reverse('request_refund', args=[self.order_item.pk])
        response = self.client.post(url)
        refund_id = response.json()["refund_id"]

        # Approve the refund
        approve_url = reverse('approve_refund', args=[refund_id])
        self.client.post(approve_url)

        # Check if the order item is refunded
        check_url = reverse('check_order_item_refunded', args=[self.order_item.pk])
        response = self.client.get(check_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["refunded"], True)

class AddCommentTests(TestCase):

    def setUp(self):
        self.customer = Customer.objects.create(
            name="John Doe", 
            tax_id="12345", 
            email="john@example.com", 
            password="password123", 
            home_address="123 Main Street"
        )
        self.product = Product.objects.create(
            model="Test Product",
            serial_number="SN123456",
            stock=10,
            warranty_status="Valid",
            distributor_info="Distributor X",
            base_price=100.00,
            price=100.00
        )
        self.order = Order.objects.create(
            customer=self.customer,
            order_date="2023-01-01",
            total_amount=100.00,
            discount_applied=0.00,
            payment_status="Paid"
        )
        OrderItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=1,
            price_per_item=100.00
        )
        self.add_comment_url = reverse('add_comment', kwargs={'product_id': self.product.product_id})



    def test_add_comment_without_purchase(self):
        new_customer = Customer.objects.create(
            name="Jane Smith", 
            tax_id="67890", 
            email="jane@example.com", 
            password="password123", 
            home_address="456 Elm Street"
        )
        data = {
            "customer_id": new_customer.customer_id,
            "comment": "I love this!"
        }
        response = self.client.post(self.add_comment_url, data, content_type="application/json")
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Comment.objects.count(), 0)


class GetCommentsTests(TestCase):

    def setUp(self):
        self.customer = Customer.objects.create(
            name="John Doe", 
            tax_id="12345", 
            email="john@example.com", 
            password="password123", 
            home_address="123 Main Street"
        )
        self.product = Product.objects.create(
            model="Test Product",
            serial_number="SN123456",
            stock=10,
            warranty_status="Valid",
            distributor_info="Distributor X",
            base_price=100.00,
            price=100.00
        )
        Comment.objects.create(
            product=self.product,
            customer=self.customer,
            comment="Pending comment",
            approval_status="Pending"
        )
        Comment.objects.create(
            product=self.product,
            customer=self.customer,
            comment="Approved comment",
            approval_status="Approved"
        )
        self.get_comments_url = reverse('get_comments', kwargs={'product_id': self.product.product_id})

    def test_get_all_comments(self):
        response = self.client.get(self.get_comments_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()["comments"]), 2)

    def test_get_approved_comments_only(self):
        response = self.client.get(f"{self.get_comments_url}?approved=true")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()["comments"]), 1)
        self.assertEqual(response.json()["comments"][0]["comment"], "Approved comment")

    def test_get_comments_no_results(self):
        another_product = Product.objects.create(
            model="Another Product",
            serial_number="SN654321",
            stock=5,
            warranty_status="Valid",
            distributor_info="Distributor Y",
            base_price=200.00,
            price=200.00
        )
        get_comments_url = reverse('get_comments', kwargs={'product_id': another_product.product_id})
        response = self.client.get(get_comments_url)
        self.assertEqual(response.status_code, 404)
        self.assertIn("No comments found", response.json()["message"])

class DeleteCommentTests(TestCase):

    def setUp(self):
        self.customer = Customer.objects.create(
            name="John Doe", 
            tax_id="12345", 
            email="john@example.com", 
            password="password123", 
            home_address="123 Main Street"
        )
        self.product = Product.objects.create(
            model="Test Product",
            serial_number="SN123456",
            stock=10,
            warranty_status="Valid",
            distributor_info="Distributor X",
            base_price=100.00,
            price=100.00,
            discount=None
        )
        self.comment = Comment.objects.create(
            product=self.product,
            customer=self.customer,
            comment="This is a test comment",
            approval_status="Pending"
        )
        self.delete_comment_url = reverse(
            'delete_comment', 
            kwargs={'product_id': self.product.product_id, 'comment_id': self.comment.comment_id}
        )

    def test_delete_comment_success(self):
        data = {"customer_id": self.customer.customer_id}
        response = self.client.delete(self.delete_comment_url, data, content_type="application/json")
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Comment.objects.count(), 0)

    def test_delete_comment_not_owner(self):
        another_customer = Customer.objects.create(
            name="Jane Smith", 
            tax_id="67890", 
            email="jane@example.com", 
            password="password123", 
            home_address="456 Elm Street"
        )
        data = {"customer_id": another_customer.customer_id}
        response = self.client.delete(self.delete_comment_url, data, content_type="application/json")
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Comment.objects.count(), 1)

    def test_delete_comment_not_found(self):
        invalid_comment_url = reverse(
            'delete_comment', 
            kwargs={'product_id': self.product.product_id, 'comment_id': 9999}
        )
        response = self.client.delete(invalid_comment_url, {}, content_type="application/json")
        self.assertEqual(response.status_code, 404)

class AddRatingTests(TestCase):
    def setUp(self):
        self.customer = Customer.objects.create(
            name="John Doe",
            tax_id="12345",
            email="john@example.com",
            password="password123",
            home_address="123 Main Street"
        )
        self.product = Product.objects.create(
            model="Test Product",
            serial_number="SN123456",
            stock=10,
            warranty_status="Valid",
            distributor_info="Distributor X",
            base_price=100.00,
            price=100.00
        )
        self.order = Order.objects.create(
            customer=self.customer,
            order_date="2023-01-01",
            total_amount=100.00,
            discount_applied=0.00,
            payment_status="Paid"
        )
        OrderItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=1,
            price_per_item=100.00
        )
        self.add_rating_url = reverse('add_rating', kwargs={'product_id': self.product.product_id})

  

    def test_add_rating_invalid_value(self):
        data = {
            "customer_id": self.customer.customer_id,
            "rating_value": 6
        }
        response = self.client.post(self.add_rating_url, data, content_type="application/json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid rating value", response.json()["error"])

    def test_add_rating_without_purchase(self):
        new_customer = Customer.objects.create(
            name="Jane Smith",
            tax_id="67890",
            email="jane@example.com",
            password="password123",
            home_address="456 Elm Street"
        )
        data = {
            "customer_id": new_customer.customer_id,
            "rating_value": 4
        }
        response = self.client.post(self.add_rating_url, data, content_type="application/json")
        self.assertEqual(response.status_code, 403)
        self.assertIn("You cannot rate a product before buying it", response.json()["error"])

    def test_add_rating_duplicate(self):
        Rating.objects.create(
            customer=self.customer,
            product=self.product,
            rating_value=4
        )
        data = {
            "customer_id": self.customer.customer_id,
            "rating_value": 3
        }
        response = self.client.post(self.add_rating_url, data, content_type="application/json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("You have already rated this product", response.json()["error"])

class GetRatingsTests(TestCase):
    def setUp(self):
        self.customer = Customer.objects.create(
            name="John Doe",
            tax_id="12345",
            email="john@example.com",
            password="password123",
            home_address="123 Main Street"
        )
        self.product = Product.objects.create(
            model="Test Product",
            serial_number="SN123456",
            stock=10,
            warranty_status="Valid",
            distributor_info="Distributor X",
            base_price=100.00,
            price=100.00,
            discount=None  # Set discount as None
        )
        Rating.objects.create(
            customer=self.customer,
            product=self.product,
            rating_value=4
        )
        Rating.objects.create(
            customer=self.customer,
            product=self.product,
            rating_value=5
        )
        self.get_ratings_url = reverse('get_ratings', kwargs={'product_id': self.product.product_id})

    def test_get_ratings_success(self):
        response = self.client.get(self.get_ratings_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()["ratings"]), 2)
        self.assertEqual(response.json()["ratings"][0]["rating_value"], 4)

    def test_get_ratings_no_ratings(self):
        another_product = Product.objects.create(
            model="Another Product",
            serial_number="SN654321",
            stock=5,
            warranty_status="Valid",
            distributor_info="Distributor Y",
            base_price=200.00,
            price=200.00
        )
        get_ratings_url = reverse('get_ratings', kwargs={'product_id': another_product.product_id})
        response = self.client.get(get_ratings_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["ratings"], [])

class DeleteRatingTests(TestCase):
    def setUp(self):
        self.customer = Customer.objects.create(
            name="John Doe",
            tax_id="12345",
            email="john@example.com",
            password="password123",
            home_address="123 Main Street"
        )
        self.product = Product.objects.create(
            model="Test Product",
            serial_number="SN123456",
            stock=10,
            warranty_status="Valid",
            distributor_info="Distributor X",
            base_price=100.00,
            price=100.00,
            discount=None
        )
        self.rating = Rating.objects.create(
            customer=self.customer,
            product=self.product,
            rating_value=5
        )
        self.delete_rating_url = reverse(
            'delete_rating',
            kwargs={'product_id': self.product.product_id, 'rating_id': self.rating.rating_id}
        )

    def test_delete_rating_success(self):
        data = {"customer_id": self.customer.customer_id}
        response = self.client.delete(self.delete_rating_url, data, content_type="application/json")
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Rating.objects.count(), 0)

    def test_delete_rating_not_owner(self):
        another_customer = Customer.objects.create(
            name="Jane Smith",
            tax_id="67890",
            email="jane@example.com",
            password="password123",
            home_address="456 Elm Street"
        )
        data = {"customer_id": another_customer.customer_id}
        response = self.client.delete(self.delete_rating_url, data, content_type="application/json")
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Rating.objects.count(), 1)

    def test_delete_rating_not_found(self):
        invalid_rating_url = reverse(
            'delete_rating',
            kwargs={'product_id': self.product.product_id, 'rating_id': 9999}
        )
        response = self.client.delete(invalid_rating_url, {}, content_type="application/json")
        self.assertEqual(response.status_code, 404)


class ListProductsTests(TestCase):
    def setUp(self):
        Product.objects.create(
            model="Product 1",
            serial_number="SN12345",
            stock=10,
            warranty_status="Valid",
            distributor_info="Distributor X",
            base_price=50.00,
            price=60.00,
            discount=None 
        )
        Product.objects.create(
            model="Product 2",
            serial_number="SN67890",
            stock=5,
            warranty_status="Expired",
            distributor_info="Distributor Y",
            base_price=100.00,
            price=120.00,
            discount=None
        )
        self.list_products_url = reverse('list_products')

    def test_list_products(self):
        response = self.client.get(self.list_products_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 2)
        self.assertEqual(response.json()[0]['model'], "Product 1")



class GetProductTests(TestCase):
    def setUp(self):
        self.product = Product.objects.create(
            model="Product 1",
            serial_number="SN12345",
            stock=10,
            warranty_status="Valid",
            distributor_info="Distributor X",
            base_price=50.00,
            price=60.00
        )
        self.get_product_url = reverse('get_product', kwargs={'product_id': self.product.product_id})

    def test_get_product_success(self):
        response = self.client.get(self.get_product_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["model"], "Product 1")

    def test_get_product_not_found(self):
        invalid_url = reverse('get_product', kwargs={'product_id': 9999})
        response = self.client.get(invalid_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

class UpdateProductTests(TestCase):
    def setUp(self):
        self.product = Product.objects.create(
            model="Product 1",
            serial_number="SN12345",
            stock=10,
            warranty_status="Valid",
            distributor_info="Distributor X",
            base_price=50.00,
            price=60.00
        )
        self.update_product_url = reverse('update_product', kwargs={'product_id': self.product.product_id})

    def test_update_product_success(self):
        data = {
            "model": "Updated Product",
            "serial_number": "SN12345",
            "stock": 20,
            "warranty_status": "Valid",
            "distributor_info": "Distributor X",
            "base_price": 50.00,
            "price": 70.00,
            "discount": None
        }
        response = self.client.put(self.update_product_url, data, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.product.refresh_from_db()
        self.assertEqual(self.product.model, "Updated Product")
        self.assertEqual(self.product.stock, 20)

    def test_update_product_invalid_data(self):
        data = {"model": ""}
        response = self.client.put(self.update_product_url, data, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class DeleteProductTests(TestCase):
    def setUp(self):
        self.product = Product.objects.create(
            model="Product 1",
            serial_number="SN12345",
            stock=10,
            warranty_status="Valid",
            distributor_info="Distributor X",
            base_price=50.00,
            price=60.00
        )
        self.delete_product_url = reverse('delete_product', kwargs={'product_id': self.product.product_id})

    def test_delete_product_success(self):
        response = self.client.delete(self.delete_product_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Product.objects.count(), 0)

    def test_delete_product_not_found(self):
        invalid_url = reverse('delete_product', kwargs={'product_id': 9999})
        response = self.client.delete(invalid_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

class SearchProductsTests(TestCase):
    def setUp(self):
        Product.objects.create(
            model="Product 1",
            serial_number="SN12345",
            description="High-quality product",
            stock=10,
            warranty_status="Valid",
            distributor_info="Distributor X",
            base_price=50.00,
            price=60.00
        )
        Product.objects.create(
            model="Amazing Product",
            serial_number="SN67890",
            description="Amazing features and design",
            stock=5,
            warranty_status="Valid",
            distributor_info="Distributor Y",
            base_price=100.00,
            price=120.00
        )
        self.search_products_url = reverse('search_products')

    def test_search_products_success(self):
        response = self.client.get(self.search_products_url + '?q=amazing')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(response.json()[0]["model"], "Amazing Product")

    def test_search_products_no_results(self):
        response = self.client.get(self.search_products_url + '?q=nonexistent')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 0)

    def test_search_products_missing_query(self):
        response = self.client.get(self.search_products_url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Search query parameter 'q' is required", response.json()["error"])

class CreateDiscountTests(TestCase):
    def setUp(self):
        # Create a Category first
        self.category = Category.objects.create(
            name="Footwear",
            description="All kinds of shoes"
        )

        # Create Products and link them to the category
        self.product1 = Product.objects.create(
            model="Product 1",
            serial_number="SN001",
            stock=10,
            warranty_status="Valid",
            distributor_info="Distributor A",
            base_price=50.00,
            price=50.00,
            category=self.category  # Link product to category
        )
        self.product2 = Product.objects.create(
            model="Product 2",
            serial_number="SN002",
            stock=20,
            warranty_status="Valid",
            distributor_info="Distributor B",
            base_price=100.00,
            price=100.00,
            category=self.category  # Link product to category
        )

        self.create_discount_url = reverse("create_discount")

    def test_create_discount_success(self):
        data = {
            "discount_name": "Winter Sale",
            "discount_rate": "0.20",  # Ensure discount_rate is a string representing a decimal
            "start_date": "2025-01-01",
            "end_date": "2025-01-15",
            "product_ids": [self.product1.product_id, self.product2.product_id]
        }
        response = self.client.post(self.create_discount_url, data, content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Discount.objects.count(), 1)
        self.assertEqual(
            Product.objects.get(product_id=self.product1.product_id).discount.discount_name,
            "Winter Sale"
        )

    def test_create_discount_missing_field(self):
        data = {
            "discount_name": "Winter Sale",
            # Missing 'discount_rate'
            "start_date": "2025-01-01",
            "end_date": "2025-01-15"
        }
        response = self.client.post(self.create_discount_url, data, content_type="application/json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("message", response.json())
        self.assertEqual(response.json()["message"], "'discount_rate'")
        
class GetDiscountTests(TestCase):
    def setUp(self):
        self.discount = Discount.objects.create(
            discount_name="Winter Sale",
            discount_rate=Decimal("0.20"),
            start_date="2025-01-01",
            end_date="2025-01-15"
        )
        self.get_discount_url = reverse("get_discount", kwargs={"discount_id": self.discount.discount_id})

    def test_get_discount_success(self):
        response = self.client.get(self.get_discount_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["discount"]["discount_name"], "Winter Sale")

    def test_get_discount_not_found(self):
        response = self.client.get(reverse("get_discount", kwargs={"discount_id": 9999}))
        self.assertEqual(response.status_code, 404)
        self.assertIn("error", response.json())


class DeleteDiscountTests(TestCase):
    def setUp(self):
        # Create a Category first
        self.category = Category.objects.create(
            name="Footwear",
            description="All kinds of shoes"
        )

        # Create Products and link them to the category, ensuring base_price is a Decimal
        self.product1 = Product.objects.create(
            model="Product 1",
            serial_number="SN001",
            stock=10,
            warranty_status="Valid",
            distributor_info="Distributor A",
            base_price=50.00,  # Using float directly, no change to model
            price=50.00,  # Using float directly, no change to model
            category=self.category  # Link product to category
        )
        self.product2 = Product.objects.create(
            model="Product 2",
            serial_number="SN002",
            stock=20,
            warranty_status="Valid",
            distributor_info="Distributor B",
            base_price=100.00,  # Using float directly, no change to model
            price=100.00,  # Using float directly, no change to model
            category=self.category  # Link product to category
        )

        # Now manually set the price to a Decimal before saving
        self.product1.price = Decimal(str(self.product1.base_price))
        self.product2.price = Decimal(str(self.product2.base_price))
        self.product1.save()
        self.product2.save()

        # Create a Discount
        self.discount = Discount.objects.create(
            discount_name="Winter Sale",
            discount_rate=Decimal("0.20"),
            start_date="2025-01-01",
            end_date="2025-01-15"
        )

        self.delete_discount_url = reverse("delete_discount", kwargs={"discount_id": self.discount.discount_id})

    def test_delete_discount_success(self):
        response = self.client.delete(self.delete_discount_url, content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Discount.objects.count(), 0)
        self.assertIsNone(Product.objects.get(product_id=self.product1.product_id).discount)

    def test_delete_discount_not_found(self):
        response = self.client.delete(reverse("delete_discount", kwargs={"discount_id": 9999}), content_type="application/json")
        self.assertEqual(response.status_code, 404)


class GetAllDiscountTests(TestCase):
    def setUp(self):
        # Create discounts
        Discount.objects.create(
            discount_name="Winter Sale",
            discount_rate="0.20",  # Ensure discount_rate is a string representing a decimal
            start_date="2025-01-01",
            end_date="2025-01-15"
        )
        Discount.objects.create(
            discount_name="Spring Sale",
            discount_rate="0.10",  # Ensure discount_rate is a string representing a decimal
            start_date="2025-03-01",
            end_date="2025-03-15"
        )

        self.get_all_discounts_url = reverse("get_all_discounts")

    def test_get_all_discounts(self):
        response = self.client.get(self.get_all_discounts_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()["discounts"]), 2)

    def test_get_all_discounts_empty(self):
        # Delete all discounts to simulate empty data
        Discount.objects.all().delete()

        response = self.client.get(self.get_all_discounts_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["discounts"], [])

class WishlistTests(TestCase):
    def setUp(self):
        # Create a Category
        self.category = Category.objects.create(
            name="Footwear",
            description="All kinds of shoes"
        )

        # Create a Customer
        self.customer = Customer.objects.create(
            customer_id=1,
            name="John Doe",
            email="johndoe@example.com",
        )

        # Ensure Wishlist exists for the Customer
        self.wishlist, created = Wishlist.objects.get_or_create(customer=self.customer)

        # Create Products and link them to the category
        self.product1 = Product.objects.create(
            model="Product 1",
            serial_number="SN001",
            stock=10,
            warranty_status="Valid",
            distributor_info="Distributor A",
            base_price=50.00,
            price=50.00,
            category=self.category
        )
        self.product2 = Product.objects.create(
            model="Product 2",
            serial_number="SN002",
            stock=20,
            warranty_status="Valid",
            distributor_info="Distributor B",
            base_price=100.00,
            price=100.00,
            category=self.category
        )

        # URL endpoints for testing
        self.add_to_wishlist_url = lambda customer_id, product_id: reverse(
            "add_to_wishlist", kwargs={"customer_id": customer_id, "product_id": product_id}
        )
        self.remove_from_wishlist_url = lambda customer_id, product_id: reverse(
            "remove_from_wishlist", kwargs={"customer_id": customer_id, "product_id": product_id}
        )
        self.get_wishlist_url = lambda customer_id: reverse(
            "get_wishlist", kwargs={"customer_id": customer_id}
        )

    def test_add_to_wishlist_success(self):
        response = self.client.post(self.add_to_wishlist_url(self.customer.customer_id, self.product1.product_id))
        self.assertEqual(response.status_code, 201)
        self.assertEqual(WishlistItem.objects.filter(wishlist=self.wishlist, product=self.product1).count(), 1)

    def test_add_to_wishlist_already_exists(self):
        # Add the product first
        WishlistItem.objects.create(wishlist=self.wishlist, product=self.product1)
        response = self.client.post(self.add_to_wishlist_url(self.customer.customer_id, self.product1.product_id))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "Product already in wishlist")

    def test_remove_from_wishlist_success(self):
        # Add the product to the wishlist
        WishlistItem.objects.create(wishlist=self.wishlist, product=self.product1)
        response = self.client.delete(self.remove_from_wishlist_url(self.customer.customer_id, self.product1.product_id))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(WishlistItem.objects.filter(wishlist=self.wishlist, product=self.product1).count(), 0)

    def test_remove_from_wishlist_not_found(self):
        response = self.client.delete(self.remove_from_wishlist_url(self.customer.customer_id, self.product1.product_id))
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["status"], "Product not found in wishlist")

    def test_get_wishlist_with_items(self):
        # Add two products to the wishlist
        WishlistItem.objects.create(wishlist=self.wishlist, product=self.product1)
        WishlistItem.objects.create(wishlist=self.wishlist, product=self.product2)
        response = self.client.get(self.get_wishlist_url(self.customer.customer_id))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()["wishlist_items"]), 2)

    def test_get_wishlist_empty(self):
        response = self.client.get(self.get_wishlist_url(self.customer.customer_id))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()["wishlist_items"]), 0)