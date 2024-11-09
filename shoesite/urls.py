# shoesite/urls.py


from django.urls import path
from shoesite.views.customer_views import get_customer, create_customer
from shoesite.views.product_views import list_products, create_product, get_product, update_product, delete_product, search_products
from shoesite.views.cart_views import add_to_cart, remove_from_cart, get_cart
from shoesite.views.wishlist_views import add_to_wishlist, remove_from_wishlist, get_wishlist
from shoesite.views.refund_views import request_refund, approve_refund



urlpatterns = [
    # Customer paths
    path('customer/<str:customer_id>/', get_customer, name='get_customer'),
    path('customer/create/', create_customer, name='create_customer'),

    # Product paths
    path('products/', list_products, name='list_products'),
    path('products/create/', create_product, name='create_product'),
    path('products/<str:product_id>/', get_product, name='get_product'),
    path('products/<str:product_id>/update/', update_product, name='update_product'),
    path('products/<str:product_id>/delete/', delete_product, name='delete_product'),
    path('products/search/', search_products, name='search_products'),

    # Shopping Cart paths
    path('cart/<str:customer_id>/add/<str:product_id>/', add_to_cart, name='add_to_cart'),
    path('cart/<str:customer_id>/remove/<str:product_id>/', remove_from_cart, name='remove_from_cart'),
    path('cart/<str:customer_id>/', get_cart, name='get_cart'),

    # Wishlist paths
    path('wishlist/<str:customer_id>/add/<str:product_id>/', add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/<str:customer_id>/remove/<str:product_id>/', remove_from_wishlist, name='remove_from_wishlist'),
    path('wishlist/<str:customer_id>/', get_wishlist, name='get_wishlist'),

    # Refund paths
    path('refund/request/<int:order_item_id>/', request_refund, name='request_refund'),
    path('refund/approve/<int:refund_id>/', approve_refund, name='approve_refund'),
]
