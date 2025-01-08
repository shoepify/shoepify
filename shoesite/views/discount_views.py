from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from shoesite.models import Discount, Product, Wishlist, WishlistItem
from django.views.decorators.csrf import csrf_exempt
import json
from django.core.mail import EmailMessage
from django.core.mail import send_mail

# Create a Discount
@csrf_exempt
def create_discount(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            discount_name = data["discount_name"]
            discount_rate = data["discount_rate"]
            start_date = data["start_date"]
            end_date = data["end_date"]
            product_ids = data.get("product_ids", [])  # Optional product list
            
            # Create the discount
            discount = Discount.objects.create(
                discount_name=discount_name,
                discount_rate=discount_rate,
                start_date=start_date,
                end_date=end_date
            )
            
            # Apply the discount to the specified products
            products = Product.objects.filter(product_id__in=product_ids)
            for product in products:
                product.discount = discount
                product.save()
            
            # Send email notifications
            notify_customers_of_discount(discount, products)

            return JsonResponse({"status": "success", "discount_id": discount.discount_id})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=400)

# Get Discount by ID
def get_discount(request, discount_id):
    try:
        discount = get_object_or_404(Discount, discount_id=discount_id)
        discount_data = {
            "discount_id": discount.discount_id,
            "discount_name": discount.discount_name,
            "discount_rate": float(discount.discount_rate),
            "start_date": discount.start_date,
            "end_date": discount.end_date
        }
        return JsonResponse({"status": "success", "discount": discount_data})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=404)

# Delete Discount
@csrf_exempt
def delete_discount(request, discount_id):
    # Retrieve the discount by ID
    discount = get_object_or_404(Discount, discount_id=discount_id)
    
    # Get all products associated with the discount
    affected_products = discount.products.all()

    # Set discount rate to 0 for each affected product
    for product in affected_products:
        # Set discount rate to 0 (no discount)
        product.discount = None
        product.save()  # Save the product to trigger recalculating the price

    # Now delete the discount from the database
    discount.delete()

    return JsonResponse({
        "status": "success",
        "message": f"Discount with ID {discount_id} deleted and prices reverted."
    })



def notify_customers_of_discount(discount, products):
    """
    Notify customers about the newly created discount for specific products.
    """
    try:
        # Find all customers with the products in their wishlists
        product_ids = [product.product_id for product in products]
        wishlist_items = WishlistItem.objects.filter(product_id__in=product_ids)
        customers = set(item.wishlist.customer for item in wishlist_items)

        # Prepare the email content
        subject = f"Exclusive Discount: {discount.discount_name}"
        message = (
            f"Dear Customer,\n\n"
            f"We're excited to offer you a discount on the following products:\n\n"
            + "\n".join([f"- {product.model}" for product in products]) +
            f"\n\nDiscount: {discount.discount_rate * 100}% off!\n"
            f"Valid from {discount.start_date} to {discount.end_date}.\n\n"
            f"Don't miss out! Visit our store now to take advantage of this special offer.\n\n"
            f"Best regards,\nBag Store Team"
        )
        from_email = 'shoesitecs@gmail.com'

        # Send emails to all relevant customers
        for customer in customers:
            send_mail(subject, message, from_email, [customer.email])
            print(f"Email sent to {customer.email}")

    except Exception as e:
        print(f"Error sending discount emails: {e}")

# Get All Discounts
def get_all_discounts(request):
    try:
        discounts = Discount.objects.all()
        discount_list = [
            {
                "discount_id": discount.discount_id,
                "discount_name": discount.discount_name,
                "discount_rate": float(discount.discount_rate),
                "start_date": discount.start_date,
                "end_date": discount.end_date,
            }
            for discount in discounts
        ]
        return JsonResponse({"status": "success", "discounts": discount_list})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)

