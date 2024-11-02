# views.py
from django.http import JsonResponse
from .models import Customer

def get_customer(request, customer_id):
    try:
        customer = Customer.objects.get(customer_id=customer_id)
        data = {
            'customer_id': customer.customer_id,
            'password': customer.password,
            'name': customer.name,
            'email': customer.email,
            'home_address': customer.home_address,
            'billing_address': customer.billing_address,
            'phone_number': customer.phone_number,
        }
        return JsonResponse(data)
    except Customer.DoesNotExist:
        return JsonResponse({'error': 'Customer not found'}, status=404)
