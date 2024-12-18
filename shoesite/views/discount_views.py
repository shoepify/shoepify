from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from shoesite.models import Discount, Product
from django.views.decorators.csrf import csrf_exempt
import json

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
            
            # Link discount to products
            for product_id in product_ids:
                product = Product.objects.get(product_id=product_id)
                product.discount = discount
                product.save()

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