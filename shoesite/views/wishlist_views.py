# views.py
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from shoesite.models import Customer, Wishlist, WishlistItem, Product  # Update to absolute import
import json
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from rest_framework.parsers import JSONParser


from shoesite.serializers import CustomerSerializer, WishlistSerializer, RefundSerializer, WishlistItemSerializer, ShoppingCartSerializer, CartItemSerializer, ProductSerializer

"""
# WISHLIST
@csrf_exempt
def add_to_wishlist(request, customer_id, product_id):
    if request.method == 'POST':
        customer = get_object_or_404(Customer, customer_id=customer_id)
        wishlist = customer.wishlist
        product = get_object_or_404(Product, product_id=product_id)

        if not WishlistItem.objects.filter(wishlist=wishlist, product=product).exists():
            WishlistItem.objects.create(wishlist=wishlist, product=product)
            return JsonResponse({'status': 'Product added to wishlist'}, status=201)
        return JsonResponse({'status': 'Product already in wishlist'}, status=200)

@csrf_exempt
def remove_from_wishlist(request, customer_id, product_id):
    if request.method == 'DELETE':
        customer = get_object_or_404(Customer, customer_id=customer_id)
        wishlist = customer.wishlist
        product = get_object_or_404(Product, product_id=product_id)

        deleted, _ = WishlistItem.objects.filter(wishlist=wishlist, product=product).delete()
        if deleted:
            return JsonResponse({'status': 'Product removed from wishlist'}, status=200)
        return JsonResponse({'status': 'Product not found in wishlist'}, status=404)

@csrf_exempt
def get_wishlist(request, customer_id):
    if request.method == 'GET':
        customer = get_object_or_404(Customer, customer_id=customer_id)
        wishlist = Wishlist.objects.filter(customer=customer).first()

        if wishlist:
            wishlist_items = wishlist.wishlistitem_set.all()
            items_data = [{'product_id': item.product.product_id, 'model': item.product.model} for item in wishlist_items]
            return JsonResponse({'customer_id': customer.customer_id, 'wishlist_items': items_data})
        else:
            return JsonResponse({'customer_id': customer.customer_id, 'wishlist_items': []})

"""
# WISHLIST
@csrf_exempt
def add_to_wishlist(request, customer_id, product_id):
    if request.method == 'POST':
        try:
            customer = get_object_or_404(Customer, customer_id=customer_id)
            wishlist = customer.wishlist  # Kullanıcıya ait wishlist'i al
            product = get_object_or_404(Product, product_id=product_id)

            # Ürün zaten wishlist'te yoksa ekleyelim
            if not WishlistItem.objects.filter(wishlist=wishlist, product=product).exists():
                WishlistItem.objects.create(wishlist=wishlist, product=product)
                return JsonResponse({'status': 'Product added to wishlist'}, status=201)
            return JsonResponse({'status': 'Product already in wishlist'}, status=200)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def remove_from_wishlist(request, customer_id, product_id):
    if request.method == 'DELETE':
        try:
            customer = get_object_or_404(Customer, customer_id=customer_id)
            wishlist = customer.wishlist
            product = get_object_or_404(Product, product_id=product_id)

            # Ürün wishlist'ten silinmişse, başarı döndürüyoruz
            deleted, _ = WishlistItem.objects.filter(wishlist=wishlist, product=product).delete()
            if deleted:
                return JsonResponse({'status': 'Product removed from wishlist'}, status=200)
            return JsonResponse({'status': 'Product not found in wishlist'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def get_wishlist(request, customer_id):
    if request.method == 'GET':
        try:
            customer = get_object_or_404(Customer, customer_id=customer_id)
            wishlist = Wishlist.objects.filter(customer=customer).first()  # İlk wishlist'i al

            if wishlist:
                wishlist_items = wishlist.wishlistitem_set.all()
                items_data = [{'product_id': item.product.product_id, 'model': item.product.model} for item in wishlist_items]
                return JsonResponse({'customer_id': customer.customer_id, 'wishlist_items': items_data})
            else:
                return JsonResponse({'customer_id': customer.customer_id, 'wishlist_items': []})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)