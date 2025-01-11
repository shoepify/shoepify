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


# Request Refund for given Order Item id
@csrf_exempt
def request_refund(request, order_item_id):
    """
    Allows a customer to request a refund for an order item if it is within 30 days of purchase.
    """
    if request.method == 'POST':
        try:
            # Fetch the order item and check if it exists
            order_item = get_object_or_404(OrderItem, pk=order_item_id)
            order_date = order_item.order.order_date
            order = order_item.order  # Get the associated order
   
            # Check if the order status is 'Delivered'
            if order.status != 'Delivered':
                return JsonResponse({'status': 'error', 'message': 'Refund can only be requested for delivered orders.'}, status=400)

            # Check if the request is within the 30-day refund window
            if (timezone.now().date() - order_date).days > 30:
                return JsonResponse({'status': 'error', 'message': 'Refund request is past the 30-day period.'}, status=400)

            # Ensure no existing refund request for this order item
            if Refund.objects.filter(order_item=order_item).exists():
                return JsonResponse({'status': 'error', 'message': 'Refund request already exists for this order item.'}, status=400)
            print("check3")
            # Create a new refund request with a Pending status
            refund = Refund.objects.create(order_item=order_item, status='Pending')
            return JsonResponse({'status': 'success', 'message': 'Refund request submitted successfully.', 'refund_id': refund.refund_id}, status=201)
        
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method. Use POST.'}, status=405)

# Approve the Refund for given Refund id
@csrf_exempt
def approve_refund(request, refund_id):
    """
    Approves a pending refund and processes the refund.
    """
    if request.method == 'POST':
        try:
            # Fetch the refund and ensure it exists
            refund = get_object_or_404(Refund, pk=refund_id)
            
            if refund.status != 'Pending':
                return JsonResponse({'status': 'error', 'message': 'Refund request is not in Pending status.'}, status=400)
            
            # Update refund status to Approved
            refund.status = 'Approved'
            refund.save()
            
            # Add the product back to stock
            product = refund.order_item.product
            product.stock += refund.order_item.quantity
            product.save()
            
            # Refund the amount to the customer's balance
            customer = refund.order_item.order.customer
            refunded_amount = refund.order_item.price_per_item * refund.order_item.quantity
            customer.balance += refunded_amount
            customer.save()

            # Mark the order item as refunded
            order_item = refund.order_item
            order_item.refunded = True
            order_item.save()
            
            # Delete the order item after processing
            #refund.order_item.delete()
            
            return JsonResponse({'status': 'success', 'message': 'Refund approved successfully.', 'refunded_amount': refunded_amount}, status=200)
        
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method. Use POST.'}, status=405)

# Disapprove the Refund for given Refund id
@csrf_exempt
def disapprove_refund(request, refund_id):
    """
    Rejects a pending refund request and marks it as Rejected.
    """
    if request.method == 'POST':
        try:
            # Fetch the refund and ensure it exists
            refund = get_object_or_404(Refund, pk=refund_id)
            
            if refund.status != 'Pending':
                return JsonResponse({'status': 'error', 'message': 'Refund request is not in Pending status.'}, status=400)
            
            # Update refund status to Rejected
            refund.status = 'Rejected'
            refund.save()
            
            return JsonResponse({'status': 'success', 'message': 'Refund request disapproved successfully.'}, status=200)
        
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method. Use POST.'}, status=405)

def get_pending_refunds(request):
    """
    Fetch refunds with a status of 'Pending' for the manager to review.
    """
    try:
        # Fetch pending refunds from the database
        pending_refunds = Refund.objects.filter(status='Pending')
        
        # Structure the data for the response
        refunds_data = [
            {
                "refund_id": refund.refund_id,
                "order_item_id": refund.order_item.order_item_id,
                "product_model": refund.order_item.product.model,
                "customer_name": refund.order_item.order.customer.name,
                "order_date": refund.order_item.order.order_date.strftime("%Y-%m-%d"),
                "quantity": refund.order_item.quantity,
                "refund_amount": float(refund.order_item.price_per_item) * refund.order_item.quantity,  # Calculate refund amount
                "created_at": refund.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            }
            for refund in pending_refunds
        ]
        
        return JsonResponse({"pending_refunds": refunds_data}, status=200)
    
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

def check_order_item_refunded(request, order_item_id):
    """
    Check whether a given order item has been refunded or not.
    """
    try:
        # Fetch the order item by ID
        order_item = get_object_or_404(OrderItem, pk=order_item_id)

        # Return the refund status
        return JsonResponse({
            "order_item_id": order_item_id,
            "order_item_model": order_item.product.model,
            "order_item_quantity": order_item.quantity,
            "refunded": order_item.refunded
        }, status=200)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

