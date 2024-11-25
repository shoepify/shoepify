from django.core.mail import EmailMessage
from rest_framework.decorators import api_view
from django.http import JsonResponse
from django.template.loader import render_to_string
from io import BytesIO
from reportlab.pdfgen import canvas
from django.conf import settings
from django.shortcuts import get_object_or_404
from shoesite.models import Order, Invoice


@api_view(['POST'])
def confirm_payment(request, order_id):
    """Simulate payment confirmation, generate invoice, and email the PDF invoice."""
    try:
        # Fetch the order
        order = get_object_or_404(Order, pk=order_id)

        # Simulate payment confirmation via mock-up banking entity
        payment_status = request.data.get('payment_status', 'Success')  # Mocked payment status
        if payment_status != 'Success':
            return JsonResponse({"error": "Payment failed"}, status=400)

        # Mark order as paid and update the order status to 'In Transit'
        order.payment_status = "Paid"
        order.status = "In Transit"  # Update order status after payment
        order.save()

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

