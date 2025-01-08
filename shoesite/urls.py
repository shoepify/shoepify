# shoesite/urls.py
from django.urls import path, include, re_path
from shoesite.views.category_views import add_category,delete_category, get_category
from shoesite.views.customer_views import get_customer, create_customer
from shoesite.views.product_views import list_products, create_product, get_product, update_product, delete_product, search_products
from shoesite.views.cart_views import add_to_cart_customer,add_to_cart_guest, get_cart_customer, get_cart_guest, place_order, complete_delivery, get_orders_by_customer, check_cart, update_order_status, get_all_orders,remove_from_cart_guest,remove_from_cart_customer, cancel_order#, remove_from_cart #, order_status
from shoesite.views.wishlist_views import add_to_wishlist, remove_from_wishlist, get_wishlist
from shoesite.views.refund_views import request_refund, approve_refund, disapprove_refund, get_pending_refunds, check_order_item_refunded
from shoesite.views.confirm_payment import confirm_payment
from shoesite.views.rating_views import add_rating, get_ratings, delete_rating
from shoesite.views.discount_views import create_discount, get_discount, delete_discount, get_all_discounts
from shoesite.views.comment_views import add_comment, get_comments, delete_comment, get_pending_comments, update_approval, disapprove_comment
from shoesite.views.auth_views import login, signup, get_tokens_for_user, test_token
from shoesite.views.customer_views import signup_customer, login_customer
from shoesite.views.pm_views import signup_product_manager, login_product_manager
from shoesite.views.sm_views import signup_sales_manager, login_sales_manager
from .views.guest_views import home_view
from shoesite.views.invoice_views import generate_pdf, send_invoice_email, create_and_send_invoice,view_invoice,view_invoices_by_date_range, create_combined_pdf, calculate_revenue_and_profit, calculate_daily_revenue_and_profit
#from .views.category_views import add_category, remove_category
from shoesite.views.invoice_views import generate_pdf, send_invoice_email, create_and_send_invoice,view_invoice, create_pdf, send_basic_email, create_pdf_ozan
#from shoesite.views import login, signup
from rest_framework_simplejwt.views import TokenRefreshView
from django.contrib import admin
from . import views
from rest_framework.routers import DefaultRouter
from . import views
from .views import product_views  # or wherever your search_products view is located
#from .views import CustomerViewSet, WishlistViewSet, RefundViewSet


"""
The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

urlpatterns = [

    # rivar login sign up
    #login path
    #re_path('login',login),
    #re_path('signup',signup),
    #re_path('test_token',test_token),
    #re_path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # login paths for customer, pm, sm
    path('login/customer/', login_customer, name='login_customer'),
    path('login/product_manager/', login_product_manager, name='login_product_manager'),
    path('login/sales_manager/', login_sales_manager, name='login_sales_manager'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # sign up paths for customer, sm, pm
    path('signup/customer/', signup_customer, name='signup_customer'),
    path('signup/sales_manager/', signup_sales_manager, name='signup_sales_manager'),
    path('signup/product_manager/', signup_product_manager, name='signup_product_manager'),
    path('', home_view, name='create_guest'),
    # customer paths
    path('customer/<int:customer_id>/', get_customer, name='get_customer'),
    path('customer/create/', create_customer, name='create_customer'),

    # sign up / login
    ## path('auth/signup/', views.sign_up, name='sign_up'),
    ## path('auth/login/', views.login, name='login'),

    # Product paths
    path('products/search/', product_views.search_products, name='search_products'),
    path('products/', list_products, name='list_products'),
    path('products/create/', create_product, name='create_product'),
    path('products/<int:product_id>/', get_product, name='get_product'),
    path('products/<int:product_id>/update/', update_product, name='update_product'),
    path('products/<int:product_id>/delete/', delete_product, name='delete_product'),
    path('products/search/', search_products, name='search_products'),

    # Shopping Cart paths
    #path('cart/<int:customer_id>/add/<int:product_id>/', add_to_cart, name='add_to_cart'),
    path('add_to_cart_guest/<int:user_id>/<int:product_id>/<int:quantity>/', add_to_cart_guest, name='add_to_cart_guest'),
    path('add_to_cart_customer/<int:user_id>/<int:product_id>/<int:quantity>/', add_to_cart_customer, name='add_to_cart_customer'),
    #path('cart/<int:customer_id>/remove/<int:product_id>/', remove_from_cart, name='remove_from_cart_guest'),
    path('customer/<int:user_id>/remove/<int:product_id>/', remove_from_cart_customer, name='remove_from_cart'),
    path('guest/<int:user_id>/remove/<int:product_id>/', remove_from_cart_guest, name='remove_from_cart'),
    path('cart_customer/<int:user_id>/', get_cart_customer, name='get_cart'),
    path('cart_guest/<int:user_id>/', get_cart_guest, name='get_cart'),
    


    # Order-related paths
    #path('order/<int:customer_id>/place/', place_order, name='place_order'),
    #path('order/<int:order_id>/status/', order_status, name='order_status'),

    # Order-related paths
    #path('order/<int:customer_id>/place/', place_order, name='place_order'),
    #path('order/<int:order_id>/status/', order_status, name='order_status'),
   

    # order related paths
    path('check_cart/<int:user_id>/', check_cart, name='check_cart'),
    path('order/place/<int:user_id>/', place_order, name='place_order'),
    path('get_orders/<int:customer_id>/', get_orders_by_customer, name='get_orders_by_customer'),
    #path('delivery/complete/<int:order_id>/', complete_delivery, name='complete_delivery'),
    path('complete_delivery/<int:order_id>/', complete_delivery, name='complete_delivery'),
    path('payment/confirm/<int:order_id>/', confirm_payment, name='confirm_payment'),
    path('invoice/create/<int:order_id>/', create_and_send_invoice, name='create_and_send_invoice'),
    path('get_all_orders/', get_all_orders, name='get_all_orders'),
    path('update_order_status/<int:order_id>/', update_order_status, name='update_order_status'),
    path('order/cancel/<int:order_id>/', cancel_order, name='cancel_order'),


    # Wishlist paths
    path('wishlist/<int:customer_id>/add/<int:product_id>/', add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/<int:customer_id>/remove/<int:product_id>/', remove_from_wishlist, name='remove_from_wishlist'),
    path('wishlist/<int:customer_id>/', get_wishlist, name='get_wishlist'),

    # Refund paths
    path('refund/request/<int:order_item_id>/', request_refund, name='request_refund'),
    path('refund/approve/<int:refund_id>/', approve_refund, name='approve_refund'),
    path('disapprove_refund/<int:refund_id>/', disapprove_refund, name='disapprove_refund'),
    path('refunds/pending/', get_pending_refunds, name='get_pending_refunds'),
    path('order-item/<int:order_item_id>/refunded/', check_order_item_refunded, name='check_order_item_refunded'),




    #comment paths
    path('products/<int:product_id>/add_comment/', add_comment, name='add_comment'),
    path('products/<int:product_id>/comments/', get_comments, name='get_comments'),
    path('products/<int:product_id>/delete_comment/<int:comment_id>/', delete_comment, name='delete_comment'),
    path('pending_comments/', get_pending_comments, name='get_pending_comments'),
    path('update_approval/<int:comment_id>/', update_approval, name='update_approval'),
    path('disapprove_comment/<int:comment_id>/', disapprove_comment, name='disapprove_comment'),
    #http://127.0.0.1:8000/products/<int:product_id>/comments/?approved=true           For approved comments

    # For adding ratings
    path('products/<int:product_id>/add_rating/', add_rating, name='add_rating'),
    path('products/<int:product_id>/ratings/', get_ratings, name='get_ratings'),
    path('products/<int:product_id>/ratings/<int:rating_id>/delete/', delete_rating, name='delete_rating'),

    #invoice mail
    path('invoice/<int:invoice_id>/view/', view_invoice, name='view_invoice'),
    path('invoice/<int:invoice_id>/email/', send_invoice_email, name='send_invoice_email'),
    path('invoice/order/<int:order_id>/create-send/', create_and_send_invoice, name='create_and_send_invoice'),
    
    #categories
    path('add-category/', add_category, name='add_category'),
    path('delete-category/<str:name>/', delete_category, name='delete_category'),
    path('get-category/<str:name>/', get_category, name='get_category'),
    #path('invoice/order/<int:order_id>/create-send/', create_and_send_invoice, name='create_and_send_invoice'),
    path('invoice/<int:invoice_id>/create-pdf/', create_pdf, name='create_pdf'),
    path('send-email/<int:customer_id>/', send_basic_email, name='send_basic_email'),
    path('invoice/<int:invoice_id>/create-pdf-ozan/', create_pdf_ozan, name='create_pdf_ozan'),


    #discount
    path('create_discount/', create_discount, name='create_discount'),
    path('get_discount/<int:discount_id>/', get_discount, name='get_discount'),
    path('delete_discount/<int:discount_id>/', delete_discount, name='delete_discount'),
    path('get_all_discounts/', get_all_discounts, name='get_all_discounts'),


    # Add to urlpatterns
    path('invoices/date-range/', view_invoices_by_date_range, name='view_invoices_by_date_range'),
    path('invoices/date-range/pdf/', create_combined_pdf, name='create_combined_pdf'),
    path('revenue/profit-loss/', calculate_revenue_and_profit, name='calculate_revenue_and_profit'),
    path('revenue/daily-revenue-profit/', calculate_daily_revenue_and_profit, name='calculate_daily_revenue_and_profit'), # plot revenue and profit chart

]


