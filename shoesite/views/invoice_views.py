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
import matplotlib
import matplotlib.pyplot as plt
import io
from django.db.models import Sum
from datetime import timedelta
from concurrent.futures import ThreadPoolExecutor
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import matplotlib.dates as mdates



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
        return JsonResponse({'invoice_id': invoice.invoice_id, 'order_id': order.order_id, "invoice_date": invoice.invoice_date,
                "total_amount": invoice.total_amount}, status=200)

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
    Calculate total revenue and profit/loss for a given date range, excluding cancelled orders
    and refunded order items.
    """
    from django.db.models import Sum, F

    try:
        # Parse start_date and end_date from GET request
        start_date = parse_date(request.GET.get('start_date'))
        end_date = parse_date(request.GET.get('end_date'))

        if not start_date or not end_date:
            return JsonResponse({"error": "Invalid or missing date range"}, status=400)

        # Filter orders to exclude those with a 'Cancelled' status
        orders = Order.objects.filter(order_date__range=(start_date, end_date)).exclude(status='Cancelled')

        # Get all order items related to the filtered orders, excluding refunded items
        order_items = (
            OrderItem.objects.filter(order__in=orders, refunded=False)
            .select_related('product')
        )

        # Total Revenue: Sum of (quantity * price_per_item) for non-refunded items
        total_revenue = order_items.aggregate(
            total_revenue=Sum(F('quantity') * F('price_per_item'))
        )['total_revenue'] or 0

        # Total Cost: Sum of (quantity * product.cost) for non-refunded items
        total_cost = sum(
            item.quantity * item.product.cost
            for item in order_items
            if item.product and item.product.cost
        )

        # Calculate profit/loss
        profit_loss = total_revenue - total_cost

        return JsonResponse({
            "total_revenue": float(total_revenue),  # Convert Decimal to float for JSON serialization
            "total_cost": float(total_cost),
            "profit_loss": float(profit_loss)
        }, status=200)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)



from django.db.models import F, Sum  # Import F for dynamic field referencing
import io  # Import for BytesIO

# Ensure matplotlib uses a non-interactive backend if running in a server environment
matplotlib.use('Agg')

@csrf_exempt
def calculate_daily_revenue_and_profit(request):
    """
    Calculate daily revenue and profit/loss for a given date range and plot both daily revenue and profit in a single plot.
    """
    try:
        # Parse start_date and end_date from GET request
        start_date_str = request.GET.get('start_date')
        end_date_str = request.GET.get('end_date')

        if not start_date_str or not end_date_str:
            return JsonResponse({"error": "Invalid or missing date range"}, status=400)

        # Convert the string dates to actual date objects
        start_date = parse_date(start_date_str)
        end_date = parse_date(end_date_str)

        if not start_date or not end_date:
            return JsonResponse({"error": "Invalid date format, use YYYY-MM-DD"}, status=400)

        # Calculate daily revenue and profit
        daily_revenue = []
        daily_profit = []
        dates = []

        current_date = start_date
        while current_date <= end_date:
            # Get orders for the current date, excluding cancelled orders
            daily_orders = Order.objects.filter(order_date=current_date).exclude(status='Cancelled')

            # Calculate daily revenue: Sum of (quantity * price_per_item) for non-refunded items
            daily_order_items = OrderItem.objects.filter(order__in=daily_orders, refunded=False).select_related('product')
            daily_total_revenue = daily_order_items.aggregate(
                total_revenue=Sum(F('quantity') * F('price_per_item'))
            )['total_revenue'] or 0

            # Calculate daily cost: Sum of (quantity * product.cost) for non-refunded items
            daily_total_cost = sum(
                item.quantity * item.product.cost
                for item in daily_order_items
                if item.product and item.product.cost
            )

            # Calculate daily profit/loss
            daily_profit_loss = daily_total_revenue - daily_total_cost

            # Store the data for plotting
            daily_revenue.append(float(daily_total_revenue))  # Convert Decimal to float
            daily_profit.append(float(daily_profit_loss))
            dates.append(current_date)

            # Move to the next day
            current_date += timedelta(days=1)

        # Plotting (unchanged)
        fig, ax1 = plt.subplots(figsize=(10, 6))

        # Plot the revenue data (on the left y-axis)
        ax1.set_xlabel('Date')
        ax1.set_ylabel('Revenue', color='tab:blue')
        ax1.plot(dates, daily_revenue, color='tab:blue', label='Daily Revenue')
        ax1.tick_params(axis='y', labelcolor='tab:blue')

        # Format the x-axis to display only the date in YYYY-MM-DD format
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        ax1.xaxis.set_major_locator(mdates.DayLocator())  # Show one tick for each day
        plt.xticks(rotation=45)

        # Create a second y-axis for the profit/loss data
        ax2 = ax1.twinx()
        ax2.set_ylabel('Profit/Loss', color='tab:green')
        ax2.plot(dates, daily_profit, color='tab:green', label='Daily Profit/Loss')
        ax2.tick_params(axis='y', labelcolor='tab:green')

        ax1.set_title(f"Daily Revenue and Profit/Loss from {start_date_str} to {end_date_str}")

        # Tight layout to avoid overlap
        plt.tight_layout()

        # Save the plot to a BytesIO object and send it as a response
        img_buf = io.BytesIO()
        fig.savefig(img_buf, format='png')
        img_buf.seek(0)

        # Create a response for the image
        response = HttpResponse(content_type='image/png')
        response['Content-Disposition'] = 'inline; filename="daily_revenue_and_profit_plots.png"'
        response.write(img_buf.read())

        return response

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
def get_daily_revenue_and_profit(request):
    """
    Calculate and return daily revenue, cost, and profit/loss for all days in the database.
    """
    try:
        # Get the earliest and latest order dates
        earliest_order = Order.objects.earliest('order_date')
        latest_order = Order.objects.latest('order_date')

        if not earliest_order or not latest_order:
            return JsonResponse({"error": "No orders available to calculate revenue and profit."}, status=404)

        start_date = earliest_order.order_date
        end_date = latest_order.order_date

        # Calculate daily revenue, cost, and profit
        data = []

        current_date = start_date
        while current_date <= end_date:
            # Get orders for the current date, excluding cancelled orders
            daily_orders = Order.objects.filter(order_date=current_date).exclude(status='Cancelled')

            # Calculate daily revenue: Sum of (quantity * price_per_item) for non-refunded items
            daily_order_items = OrderItem.objects.filter(order__in=daily_orders, refunded=False).select_related('product')
            daily_total_revenue = daily_order_items.aggregate(
                total_revenue=Sum(F('quantity') * F('price_per_item'))
            )['total_revenue'] or 0

            # Calculate daily cost: Sum of (quantity * product.cost) for non-refunded items
            daily_total_cost = sum(
                item.quantity * item.product.cost
                for item in daily_order_items
                if item.product and item.product.cost
            )

            # Calculate daily profit/loss
            daily_profit_loss = daily_total_revenue - daily_total_cost

            # Append to data list
            data.append({
                "date": current_date.strftime('%Y-%m-%d'),
                "daily_revenue": float(daily_total_revenue),  # Convert Decimal to float
                "daily_cost": float(daily_total_cost),
                "daily_profit": float(daily_profit_loss),
            })

            # Move to the next day
            current_date += timedelta(days=1)

        return JsonResponse({"data": data}, status=200)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


import json
from datetime import datetime

@csrf_exempt
def update_invoice_date(request, invoice_id):
    if request.method == 'POST':
        try:
            # Parse the JSON body
            data = json.loads(request.body)
            new_date = data.get('invoice_date')

            # Validate the date format
            try:
                new_date = datetime.strptime(new_date, "%Y-%m-%d").date()
            except ValueError:
                return JsonResponse({'error': 'Invalid date format. Use YYYY-MM-DD.'}, status=400)

            # Query using the correct field 'invoice_id'
            invoice = Invoice.objects.get(invoice_id=invoice_id)
            invoice.invoice_date = new_date
            invoice.save()

            return JsonResponse({
                'message': 'Invoice date updated successfully.',
                'invoice_id': invoice_id,
                'new_date': str(new_date)
            }, status=200)

        except Invoice.DoesNotExist:
            return JsonResponse({'error': 'Invoice not found.'}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON body.'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Only POST requests are allowed.'}, status=405)
