# views/__init__.py

from .rating_views import add_rating
from .cart_views import add_to_cart, remove_from_cart, get_cart
from .wishlist_views import add_to_wishlist, remove_from_wishlist, get_wishlist
from .refund_views import request_refund, approve_refund
from .product_views import create_product, get_product, update_product, delete_product, list_products, search_products
#from .views import login, signup, test_token, get_customer, create_customer

# Add other imports as needed