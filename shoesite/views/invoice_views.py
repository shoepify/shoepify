from django.template.loader import render_to_string
from xhtml2pdf import pisa
from django.http import HttpResponse, JsonResponse
from django.core.mail import EmailMessage
from io import BytesIO
from django.shortcuts import get_object_or_404
from shoesite.models import Invoice, Order  # Update these imports to match your actual models
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt


# Generate PDF from HTML
def generate_pdf(html_content):
    """
    Generate a PDF from HTML content.
    """
    pdf_buffer = BytesIO()
    pisa_status = pisa.CreatePDF(html_content, dest=pdf_buffer)
    if pisa_status.err:
        return None
    pdf_buffer.seek(0)
    return pdf_buffer


# Create PDF for Invoice
def create_pdf(request, invoice_id):
    """Generate a PDF for the specified invoice."""
    try:
        # Fetch the invoice
        invoice = get_object_or_404(Invoice, invoice_id=invoice_id)
        
        # Prepare context for rendering the template
        context = {'invoice': invoice, 'order': invoice.order}

        # Render the invoice template with the context
        html_content = render_to_string('invoice_template.html', context)

        # Create a BytesIO buffer to hold the PDF
        pdf_buffer = BytesIO()
        pisa_status = pisa.CreatePDF(html_content, dest=pdf_buffer)

        if pisa_status.err:
            return HttpResponse('Error generating PDF', status=500)

        # Return the generated PDF as an HTTP response
        pdf_buffer.seek(0)
        return HttpResponse(pdf_buffer, content_type='application/pdf')

    except Exception as e:
        return HttpResponse(f"Error: {str(e)}", status=500)


# View Invoice (JSON Details Only)
@csrf_exempt
def view_invoice(request, invoice_id):
    """
    Retrieve and return the invoice details using the provided invoice_id.
    """
    try:
        invoice = get_object_or_404(Invoice, invoice_id=invoice_id)
        order = invoice.order
        return JsonResponse({'invoice_id': invoice.invoice_id, 'order_id': order.order_id}, status=200)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# Send Invoice via Email
def send_invoice_email(request, invoice_id):
    """
    Send the invoice as an email with a PDF attachment.
    """
    try:
        invoice = get_object_or_404(Invoice, invoice_id=invoice_id)
        order = invoice.order

        # Render the invoice template with context
        html_content = render_to_string('invoice_template.html', {'invoice': invoice, 'order': order})

        # Generate the PDF
        pdf_buffer = generate_pdf(html_content)
        if not pdf_buffer:
            return HttpResponse('Error generating PDF', status=500)

        # Attach the PDF to an email
        email = EmailMessage(
            subject=f"Invoice #{invoice.invoice_id}",
            body="Please find your invoice attached.",
            from_email="your_email@example.com",  # Replace with your email
            to=[order.customer.email],  # Assuming the Order model has a customer email field
        )
        email.attach(f"invoice_{invoice.invoice_id}.pdf", pdf_buffer.getvalue(), 'application/pdf')
        email.send()

        return HttpResponse(f"Invoice #{invoice.invoice_id} sent to {order.customer.email}")

    except Exception as e:
        return HttpResponse(f"Error: {str(e)}", status=500)


# Create and Send Invoice (Combined)
def create_and_send_invoice(request, order_id):
    """
    Create an invoice for a given order, generate a PDF, and send it via email.
    """
    try:
        order = get_object_or_404(Order, pk=order_id)

        # Create an invoice for the order
        invoice = Invoice.objects.create(
            order=order,
            invoice_date=timezone.now().date(),
            total_amount=order.total_amount
        )

        # Render the invoice template with context
        html_content = render_to_string('invoice_template.html', {'invoice': invoice, 'order': order})

        # Generate the PDF
        pdf_buffer = generate_pdf(html_content)
        if not pdf_buffer:
            return JsonResponse({"error": "Invoice PDF generation failed."}, status=500)

        # Send the email with the PDF attached
        email = EmailMessage(
            subject=f"Invoice #{invoice.invoice_id}",
            body="Please find your invoice attached.",
            from_email="your_email@example.com",  # Replace with your email
            to=[order.customer.email],  # Assuming the Order model has a customer email field
        )
        email.attach(f"invoice_{invoice.invoice_id}.pdf", pdf_buffer.getvalue(), 'application/pdf')
        email.send()

        return JsonResponse({"message": f"Invoice #{invoice.invoice_id} created and sent to {order.customer.email}"}, status=200)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)