from rest_framework import status
from rest_framework.test import APITestCase
from shoesite.models import Customer
from django.contrib.auth.hashers import make_password

class CustomerAuthTests(APITestCase):
    def setUp(self):
        # Create a customer to use for login tests
        self.customer_data = {
            'name': 'John Doe',
            'email': 'johndoe@example.com',
            'password': 'password123',
            'tax_id': '12345',
            'home_address': '123 Elm St',
        }
        self.customer = Customer.objects.create(
            name=self.customer_data['name'],
            email=self.customer_data['email'],
            password=make_password(self.customer_data['password']),
            tax_id=self.customer_data['tax_id'],
            home_address=self.customer_data['home_address']
        )
        self.login_url = '/api/login/'  # Replace with your actual login endpoint URL
        self.signup_url = '/api/signup/'  # Replace with your actual signup endpoint URL

    # Test signup with valid data
    def test_signup_customer(self):
        response = self.client.post(self.signup_url, self.customer_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('tokens', response.data)
        self.assertIn('customer_id', response.data)

    # Test signup with missing required fields
    def test_signup_missing_field(self):
        # Missing password
        incomplete_data = self.customer_data.copy()
        del incomplete_data['password']
        response = self.client.post(self.signup_url, incomplete_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # Test login with valid credentials
    def test_login_customer(self):
        login_data = {
            'email': self.customer_data['email'],
            'password': self.customer_data['password']
        }
        response = self.client.post(self.login_url, login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('tokens', response.data)
        self.assertIn('user', response.data)

    # Test login with invalid credentials (wrong email)
    def test_login_invalid_email(self):
        login_data = {
            'email': 'wrongemail@example.com',
            'password': self.customer_data['password']
        }
        response = self.client.post(self.login_url, login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('error', response.data)

    # Test login with invalid credentials (wrong password)
    def test_login_invalid_password(self):
        login_data = {
            'email': self.customer_data['email'],
            'password': 'wrongpassword'
        }
        response = self.client.post(self.login_url, login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('error', response.data)

    # Test login with missing credentials (missing email)
    def test_login_missing_email(self):
        login_data = {
            'password': self.customer_data['password']
        }
        response = self.client.post(self.login_url, login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    # Test login with missing credentials (missing password)
    def test_login_missing_password(self):
        login_data = {
            'email': self.customer_data['email']
        }
        response = self.client.post(self.login_url, login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
