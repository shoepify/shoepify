from django.template.loader import render_to_string
from xhtml2pdf import pisa
from django.http import HttpResponse
from django.core.mail import EmailMessage
from io import BytesIO
from django.shortcuts import get_object_or_404
from shoesite.models import Invoice, Order  # Update these imports to match your actual models


# Generate PDF from HTML
def generate_pdf(html_content):
    # Create a BytesIO buffer to hold the PDF
    pdf_buffer = BytesIO()
    # Generate the PDF using xhtml2pdf
    pisa_status = pisa.CreatePDF(html_content, dest=pdf_buffer)
    # Check for errors
    if pisa_status.err:
        return None
    pdf_buffer.seek(0)
    return pdf_buffer


# View Invoice (Generate and return the PDF for display in the browser)
def view_invoice(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id)
    order = invoice.order  # Assuming an Invoice is linked to an Order

    # Render the invoice template with context
    html_content = render_to_string('invoice_template.html', {'invoice': invoice, 'order': order})

    # Generate the PDF
    pdf_buffer = generate_pdf(html_content)
    if not pdf_buffer:
        return HttpResponse('Error generating PDF', status=500)

    # Return the PDF as an HTTP response
    response = HttpResponse(pdf_buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="invoice_{invoice.id}.pdf"'
    return response


# Send Invoice via Email
def send_invoice_email(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id)
    order = invoice.order  # Assuming an Invoice is linked to an Order

    # Render the invoice template with context
    html_content = render_to_string('invoice_template.html', {'invoice': invoice, 'order': order})

    # Generate the PDF
    pdf_buffer = generate_pdf(html_content)
    if not pdf_buffer:
        return HttpResponse('Error generating PDF', status=500)

    # Attach the PDF to an email
    email = EmailMessage(
        subject=f"Invoice #{invoice.id}",
        body="Please find your invoice attached.",
        from_email="your_email@example.com",  # Replace with your email
        to=[order.customer.email],  # Assuming the Order model has a customer email field
    )
    email.attach(f"invoice_{invoice.id}.pdf", pdf_buffer.getvalue(), 'application/pdf')
    email.send()

    return HttpResponse(f"Invoice #{invoice.id} sent to {order.customer.email}")


# Generate and Email Invoice (Combined)
def create_and_send_invoice(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    # Create a new invoice (or fetch an existing one)
    invoice, created = Invoice.objects.get_or_create(order=order)

    # Render the invoice template with context
    html_content = render_to_string('invoice_template.html', {'invoice': invoice, 'order': order})

    # Generate the PDF
    pdf_buffer = generate_pdf(html_content)
    if not pdf_buffer:
        return HttpResponse('Error generating PDF', status=500)

    # Attach the PDF to an email
    email = EmailMessage(
        subject=f"Invoice #{invoice.id}",
        body="Please find your invoice attached.",
        from_email="your_email@example.com",  # Replace with your email
        to=[order.customer.email],  # Assuming the Order model has a customer email field
    )
    email.attach(f"invoice_{invoice.id}.pdf", pdf_buffer.getvalue(), 'application/pdf')
    email.send()

    return HttpResponse(f"Invoice #{invoice.id} created and sent to {order.customer.email}")
