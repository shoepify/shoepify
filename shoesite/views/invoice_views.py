from django.template.loader import render_to_string
from xhtml2pdf import pisa
from django.http import HttpResponse, JsonResponse
from django.core.mail import EmailMessage, send_mail
from io import BytesIO
from django.shortcuts import get_object_or_404
from shoesite.models import Invoice, Order, Customer, EmailPreview # Update these imports to match your actual models
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render


'''
@csrf_exempt
def send_basic_email(request, customer_id):
    # Fetch the customer
    customer = get_object_or_404(Customer, customer_id=customer_id)

    # Email details
    subject = "Thank you for ordering with us!"
    message = f"Hello {customer.name},\n\nThank you for your recent order! We appreciate your business and hope to serve you again soon!"
    from_email = "shoesitecs@gmail.com"  # Your email (sender)

    # Render the email preview instead of sending it
    return render(request, 'email_preview.html', {
        'subject': subject,
        'message': message,
        'from_email': from_email,
        'to_email': customer.email,
    })
'''
@csrf_exempt
def email_preview(request):
    emails = EmailPreview.objects.all()
    return render(request, 'email_preview.html', {'emails': emails})

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


# send basic email
@csrf_exempt
def send_basic_email(request, customer_id):
    # Fetch the customer
    customer = get_object_or_404(Customer, customer_id=customer_id)

    # Email details
    subject = "Welcome to Our Store"
    message = f"Hello {customer.name},\n\nThank you for joining us!"
    from_email = "shoesitecs@gmail.com"  # Your email (must match EMAIL_HOST_USER)
    recipient_list = [customer.email]

    # Send email
    try:
        send_mail(subject, message, from_email, recipient_list, fail_silently=False)
        return HttpResponse(f"Email successfully sent to {customer.email}")
    except Exception as e:
        return HttpResponse(f"Failed to send email: {e}", status=500)


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


def create_and_send_invoice(request, order_id):
    try:
        # Fetch the order
        order = get_object_or_404(Order, pk=order_id)

        # Create an invoice for the order
        invoice = Invoice.objects.create(
            order=order,
            invoice_date=timezone.now().date(),
            total_amount=order.total_amount
        )

        # If you are generating a PDF or sending it, make sure this part is correct
        # Example: pdf = generate_pdf(invoice)
        # send_invoice_pdf(invoice, pdf)

        # Here you can check if the invoice is created successfully
        return JsonResponse({"message": "Invoice generated and sent."}, status=200)
    
    except Exception as e:
        print(f"Error: {str(e)}")  # Log the error for debugging
        return JsonResponse({"error": f"Invoice generation failed: {str(e)}"}, status=500)