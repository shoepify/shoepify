# views.py
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from shoesite.models import Refund, OrderItem  # Update to absolute import
import json
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from rest_framework.parsers import JSONParser


from shoesite.serializers import CustomerSerializer, WishlistSerializer, RefundSerializer, WishlistItemSerializer, ShoppingCartSerializer, CartItemSerializer, ProductSerializer


# Traditional views for Refund
@csrf_exempt
def request_refund(request, order_item_id):
    if request.method == 'POST':
        order_item = get_object_or_404(OrderItem, pk=order_item_id)
        order_date = order_item.order.order_date

        if (timezone.now().date() - order_date).days > 30:
            return JsonResponse({'status': 'error', 'message': 'Refund request is past the 30-day period.'}, status=400)

        if Refund.objects.filter(order_item=order_item).exists():
            return JsonResponse({'status': 'error', 'message': 'Refund request already exists for this order item.'}, status=400)

        refund = Refund(order_item=order_item, status='Pending')
        refund.save()
        return JsonResponse({'status': 'success', 'message': 'Refund request submitted successfully.'}, status=201)

@csrf_exempt
def approve_refund(request, refund_id):
    if request.method == 'POST':
        refund = get_object_or_404(Refund, pk=refund_id)

        if refund.status != 'Pending':
            return JsonResponse({'status': 'error', 'message': 'Refund request has already been processed.'}, status=400)

        refund.approve_refund()  # Calls the approve_refund method in the Refund model
        return JsonResponse({'status': 'success', 'message': 'Refund approved successfully.', 'refunded_amount': refund.refunded_amount}, status=200)

# Make sure to define the URL patterns for these new views in your urls.py