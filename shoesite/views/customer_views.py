# views.py
from django.views.decorators.csrf import csrf_exempt
import json
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from shoesite.models import Customer  # Update to absolute import


from shoesite.serializers import CustomerSerializer, WishlistSerializer, RefundSerializer, WishlistItemSerializer, ShoppingCartSerializer, CartItemSerializer, ProductSerializer


# CUSTOMER
@csrf_exempt
def get_customer(request, customer_id):
    if request.method == 'GET':
        customer = get_object_or_404(Customer, customer_id=customer_id)
        return JsonResponse({'customer_id': customer.customer_id, 'name': customer.name})

@csrf_exempt
def create_customer(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        serializer = CustomerSerializer(data=data)
        if serializer.is_valid():
            customer = serializer.save()
            return JsonResponse({'message': 'Customer created successfully', 'customer_id': customer.customer_id}, status=201)
        return JsonResponse(serializer.errors, status=400)