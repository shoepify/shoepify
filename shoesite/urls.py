# shoesite/urls.py


from django.urls import path, include, re_path
from shoesite.views.customer_views import get_customer, create_customer
from shoesite.views.product_views import list_products, create_product, get_product, update_product, delete_product, search_products
from shoesite.views.cart_views import add_to_cart, remove_from_cart, get_cart
from shoesite.views.wishlist_views import add_to_wishlist, remove_from_wishlist, get_wishlist
from shoesite.views.refund_views import request_refund, approve_refund
from shoesite.views.rating_views import add_rating, get_ratings, delete_rating
from shoesite.views.comment_views import add_comment, get_comments, delete_comment
from shoesite.views.auth_views import login, signup, get_tokens_for_user, test_token
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

    #login path
    re_path('login',login),
    re_path('signup',signup),
    re_path('test_token',test_token),
    re_path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

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
    path('cart/<int:customer_id>/add/<int:product_id>/', add_to_cart, name='add_to_cart'),
    path('cart/<int:customer_id>/remove/<int:product_id>/', remove_from_cart, name='remove_from_cart'),
    path('cart/<int:customer_id>/', get_cart, name='get_cart'),

    # Wishlist paths
    path('wishlist/<int:customer_id>/add/<int:product_id>/', add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/<int:customer_id>/remove/<int:product_id>/', remove_from_wishlist, name='remove_from_wishlist'),
    path('wishlist/<int:customer_id>/', get_wishlist, name='get_wishlist'),

    # Refund paths
    path('refund/request/<int:order_item_id>/', request_refund, name='request_refund'),
    path('refund/approve/<int:refund_id>/', approve_refund, name='approve_refund'),

    #comment paths
    path('products/<int:product_id>/add_comment/', add_comment, name='add_comment'),
    path('products/<int:product_id>/comments/', get_comments, name='get_comments'),
    path('products/<int:product_id>/delete_comment/<int:comment_id>/', delete_comment, name='delete_comment'),

    # For adding ratings
    path('products/<int:product_id>/add_rating/', add_rating, name='add_rating'),
    path('products/<int:product_id>/ratings/', get_ratings, name='get_ratings'),
    path('products/<int:product_id>/ratings/<int:rating_id>/delete/', delete_rating, name='delete_rating'),
]
