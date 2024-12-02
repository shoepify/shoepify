from django.core.mail import EmailMessage
from rest_framework.decorators import api_view, permission_classes
from django.http import JsonResponse
from django.template.loader import render_to_string
from io import BytesIO
from reportlab.pdfgen import canvas
from django.conf import settings
from django.shortcuts import get_object_or_404
from shoesite.models import Order, Invoice
from rest_framework.permissions import AllowAny


@api_view(['POST'])
@permission_classes([AllowAny])  # This allows access without authentication
def confirm_payment(request, order_id):
    """Simulate payment confirmation, generate invoice, and email the PDF invoice."""
    try:
        # Fetch the order
        order = get_object_or_404(Order, pk=order_id)

        # Extract payment status from the request
        payment_status = request.data.get('payment_status', 'Success')  # Default to 'Success' if not provided
        if payment_status != 'Success':
            return JsonResponse({"error": "Payment failed"}, status=400)

        # Mark the order as paid and update the order status to 'In Transit'
        order.payment_status = "Paid"
        order.status = "In Transit"  # Update order status after payment
        order.save()

        return JsonResponse({"message": "Payment confirmed and order updated."}, status=200)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)