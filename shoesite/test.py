from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from .models import Customer, Product, ShoppingCart, CartItem, Wishlist, Comment, Rating, OrderItem, Order, Discount, Category, WishlistItem
from django.contrib.contenttypes.models import ContentType
from decimal import Decimal




class CategoryTests(TestCase):
    def setUp(self):
        # Create a Category
        self.category1 = Category.objects.create(
            name="Electronics",
            description="Electronic gadgets and devices"
        )
        self.category2 = Category.objects.create(
            name="Footwear",
            description="All kinds of shoes"
        )

        # Create Products linked to categories
        self.product1 = Product.objects.create(
            model="Smartphone",
            serial_number="SN001",
            stock=10,
            price=500.00,
            description="A high-end smartphone",
            category=self.category1
        )
        self.product2 = Product.objects.create(
            model="Running Shoes",
            serial_number="SN002",
            stock=20,
            price=100.00,
            description="Comfortable running shoes",
            category=self.category2
        )

        # URL endpoints for testing
        self.add_category_url = reverse("add_category")
        self.delete_category_url = lambda name: reverse("delete_category", kwargs={"name": name})
        self.get_category_url = lambda name: reverse("get_category", kwargs={"name": name})
        self.list_categories_url = reverse("list_categories")

        self.client = APIClient()

    def test_add_category_success(self):
        response = self.client.post(self.add_category_url, {
            "name": "Books",
            "description": "Various books and novels"
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["message"], "Category created successfully.")
        self.assertTrue(Category.objects.filter(name="Books").exists())

    def test_add_category_duplicate(self):
        response = self.client.post(self.add_category_url, {
            "name": "Electronics",
            "description": "Duplicate category"
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], "Category with this name already exists.")


    def test_delete_category_not_found(self):
        response = self.client.delete(self.delete_category_url("NonExistent"))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["error"], "Category not found.")

    def test_get_category_success(self):
        response = self.client.get(self.get_category_url("Electronics"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["category"]["name"], "Electronics")
        self.assertEqual(len(response.data["products"]), 1)
        self.assertEqual(response.data["products"][0]["model"], "Smartphone")

    def test_get_category_not_found(self):
        response = self.client.get(self.get_category_url("NonExistent"))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["error"], "Category not found.")

    def test_delete_category_success(self):
        # Remove related products first
        Product.objects.filter(category=self.category2).delete()
        response = self.client.delete(self.delete_category_url("Footwear"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Category deleted successfully.")
        self.assertFalse(Category.objects.filter(name="Footwear").exists())
    
    def test_list_categories_empty(self):
        # Delete all related products first
        Product.objects.all().delete()
        # Now delete categories
        Category.objects.all().delete()
        response = self.client.get(self.list_categories_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("categories", response.data)
        self.assertEqual(len(response.data["categories"]), 0)