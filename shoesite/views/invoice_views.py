from django.template.loader import render_to_string
from xhtml2pdf import pisa
from django.http import HttpResponse, JsonResponse
from django.core.mail import EmailMessage, send_mail
from io import BytesIO
from django.shortcuts import get_object_or_404
from shoesite.models import Invoice, Order, Customer, OrderItem  # Update these imports to match your actual models
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Sum
from django.utils.dateparse import parse_date



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
        return pdf_buffer
        # Ozan'ın versiyon 
        #return HttpResponse(pdf_buffer, content_type='application/pdf')

    except Exception as e:
        return HttpResponse(f"Error: {str(e)}", status=500)

# Create PDF for Invoice
def create_pdf_ozan(request, invoice_id):
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
        #return pdf_buffer
        # Ozan'ın versiyon 
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
    """
    Send the invoice as an email with a PDF attachment.
    """
    try:
        invoice = get_object_or_404(Invoice, invoice_id=invoice_id)
        order = invoice.order

        # Render the invoice template with context
        html_content = render_to_string('invoice_template.html', {'invoice': invoice, 'order': order})

        # Generate the PDF
        pdf_buffer = create_pdf(request, invoice.invoice_id)
        if not isinstance(pdf_buffer, BytesIO):
            print("PDF generation failed or returned unexpected result.")  # Debugging
            return JsonResponse({"error": "Invoice PDF generation failed."}, status=500)

        # Attach the PDF to an email
        email = EmailMessage(
            subject=f"Invoice #{invoice.invoice_id}",
            body="Please find your invoice attached.",
            from_email="shoesitecs@gmail.com",  # Replace with your email
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

        # Use create_pdf to generate the PDF and get the BytesIO buffer
        pdf_buffer = create_pdf(request, invoice.invoice_id)
        if not isinstance(pdf_buffer, BytesIO):
            return JsonResponse({"error": "Invoice PDF generation failed."}, status=500)

        # Send the email with the PDF attached
        email = EmailMessage(
            subject=f"Invoice #{invoice.invoice_id}",
            body="Please find your invoice attached.",
            from_email="shoesitecs@gmail.com",  # Replace with your email
            to=[order.customer.email],  # Assuming the Order model has a customer email field
        )
        email.attach(f"invoice_{invoice.invoice_id}.pdf", pdf_buffer.getvalue(), 'application/pdf')
        email.send()
    
        return JsonResponse({"message": f"Invoice #{invoice.invoice_id} created and sent to {order.customer.email}"}, status=200)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    

@csrf_exempt
def view_invoices_by_date_range(request):
    """
    Retrieve all invoices in a given date range.
    """
    try:
        start_date = parse_date(request.GET.get('start_date'))
        end_date = parse_date(request.GET.get('end_date'))

        if not start_date or not end_date:
            return JsonResponse({"error": "Invalid or missing date range"}, status=400)

        invoices = Invoice.objects.filter(invoice_date__range=(start_date, end_date))
        invoice_list = [
            {
                "invoice_id": invoice.invoice_id,
                "order_id": invoice.order.order_id,
                "invoice_date": invoice.invoice_date,
                "total_amount": invoice.total_amount
            }
            for invoice in invoices
        ]

        return JsonResponse({"invoices": invoice_list}, status=200)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    


@csrf_exempt
def create_combined_pdf(request):
    try:
        start_date = parse_date(request.GET.get('start_date'))
        end_date = parse_date(request.GET.get('end_date'))

        if not start_date or not end_date:
            return HttpResponse("Invalid or missing date range", status=400)

        invoices = Invoice.objects.filter(invoice_date__range=(start_date, end_date))

        # Prepare context
        context = {"invoices": invoices}

        # Load the HTML template
        html_content = render_to_string("combined_invoice_template.html", context)

        # Generate PDF
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="combined_invoices.pdf"'
        pisa_status = pisa.CreatePDF(html_content, dest=response)

        if pisa_status.err:
            return HttpResponse("Error generating PDF", status=500)

        return response
    except Exception as e:
        return HttpResponse(f"Error: {str(e)}", status=500)
    

@csrf_exempt
def calculate_revenue_and_profit(request):
    """
    Calculate total revenue and profit/loss for a given date range.
    """
    from django.db.models import Sum

    try:
        # Parse start_date and end_date from GET request
        start_date = parse_date(request.GET.get('start_date'))
        end_date = parse_date(request.GET.get('end_date'))

        if not start_date or not end_date:
            return JsonResponse({"error": "Invalid or missing date range"}, status=400)

        # Total Revenue: Sum of total_amount from orders in the given date range
        total_revenue = Order.objects.filter(order_date__range=(start_date, end_date)) \
                            .aggregate(Sum('total_amount'))['total_amount__sum'] or 0

        # Total Cost: Calculate dynamically using OrderItem and Product relationship
        order_items = OrderItem.objects.filter(order__order_date__range=(start_date, end_date)) \
            .select_related('product')

        total_cost = sum(
            item.quantity * item.product.cost for item in order_items if item.product and item.product.cost
        )

        # Calculate profit/loss
        profit_loss = total_revenue - total_cost

        return JsonResponse({
            "total_revenue": total_revenue,
            "total_cost": total_cost,
            "profit_loss": profit_loss
        }, status=200)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)