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

        # Mark order as paid
        order.payment_status = "Paid"
        order.save()

        # Generate Invoice Data
        invoice_data = {
            "order_id": order.id,
            "customer_name": order.customer.name,
            "customer_email": order.customer.email,
            "total_amount": order.total_amount,
            "items": [
                {
                    "product_name": item.product.model,
                    "quantity": item.quantity,
                    "price_per_item": item.price,
                    "total_price": item.quantity * item.price,
                }
                for item in order.orderitem_set.all()
            ]
        }

        # Generate Invoice PDF
        pdf_buffer = BytesIO()
        p = canvas.Canvas(pdf_buffer)
        p.drawString(100, 800, f"Invoice for Order ID: {invoice_data['order_id']}")
        p.drawString(100, 780, f"Customer: {invoice_data['customer_name']}")
        p.drawString(100, 760, f"Email: {invoice_data['customer_email']}")
        p.drawString(100, 740, f"Total Amount: ${invoice_data['total_amount']:.2f}")
        p.drawString(100, 720, "Items:")
        y = 700
        for item in invoice_data["items"]:
            p.drawString(120, y, f"{item['product_name']} (x{item['quantity']}) - ${item['total_price']:.2f}")
            y -= 20
        p.save()
        pdf_buffer.seek(0)

        # Save Invoice to the Database
        invoice = Invoice.objects.create(order=order, pdf_file=pdf_buffer.getvalue())
        invoice.save()

        # Send Invoice PDF via Email
        email = EmailMessage(
            subject=f"Invoice for Order #{order.id}",
            body=f"Dear {order.customer.name},\n\nPlease find your invoice attached.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[order.customer.email],
        )
        email.attach(f"Invoice_Order_{order.id}.pdf", pdf_buffer.getvalue(), "application/pdf")
        email.send()

        return JsonResponse({
            "message": "Payment confirmed and invoice sent via email.",
            "invoice_data": invoice_data,
        })

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
