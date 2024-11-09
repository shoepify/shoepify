# views.py
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from .models import Customer, OrderItem, Refund, Product, Wishlist, WishlistItem, ShoppingCart, CartItem
import json
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from rest_framework.parsers import JSONParser


from .serializers import CustomerSerializer, WishlistSerializer, RefundSerializer, WishlistItemSerializer, ShoppingCartSerializer, CartItemSerializer, ProductSerializer



# SHOPPING CART, CART ITEMS
@csrf_exempt
def add_to_cart(request, customer_id, product_id):
    if request.method == 'POST':
        data = JSONParser().parse(request)
        quantity = data.get('quantity', 1)  # Default quantity is 1 if not provided

        customer = get_object_or_404(Customer, customer_id=customer_id)
        cart, created = ShoppingCart.objects.get_or_create(customer=customer)
        product = get_object_or_404(Product, product_id=product_id)

        cart_item, item_created = CartItem.objects.get_or_create(cart=cart, product=product)

        if item_created:
            # Set the quantity for the new cart item
            cart_item.quantity = quantity
        else:
            # Increment quantity if the item already exists
            cart_item.quantity += quantity

        # Save the cart item regardless of whether it was created or updated
        cart_item.save()

        return JsonResponse({'status': 'Product added to cart'}, status=status.HTTP_201_CREATED)

@csrf_exempt
def remove_from_cart(request, customer_id, product_id):
    if request.method == 'DELETE':
        customer = get_object_or_404(Customer, customer_id=customer_id)
        cart = get_object_or_404(ShoppingCart, customer=customer)
        product = get_object_or_404(Product, product_id=product_id)

        deleted, _ = CartItem.objects.filter(cart=cart, product=product).delete()
        if deleted:
            return HttpResponse(status=status.HTTP_204_NO_CONTENT)  # Use HttpResponse for 204 No Content
        return JsonResponse({'status': 'Product not found in cart'}, status=status.HTTP_404_NOT_FOUND)

    # If the request method is not DELETE, you can return a method not allowed response
    return JsonResponse({'error': 'Method not allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
@csrf_exempt
def get_cart(request, customer_id):
    if request.method == 'GET':
        customer = get_object_or_404(Customer, customer_id=customer_id)
        cart = ShoppingCart.objects.filter(customer=customer).first()

        if cart:
            serializer = ShoppingCartSerializer(cart)
            return JsonResponse(serializer.data, safe=False, status=status.HTTP_200_OK)
        else:
            return JsonResponse({'status': 'Cart not found'}, status=status.HTTP_404_NOT_FOUND)
