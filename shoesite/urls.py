"""
URL configuration for shoesite project.

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
# urls.py
from rest_framework_simplejwt.views import TokenRefreshView
from django.contrib import admin
from django.urls import path, include, re_path
from . import views
from rest_framework.routers import DefaultRouter

#from .views import CustomerViewSet, WishlistViewSet, RefundViewSet

from .views import get_customer, create_customer, add_to_cart,  add_to_wishlist, remove_from_cart, get_cart, remove_from_wishlist, get_wishlist, request_refund, approve_refund, create_product, get_product, update_product, delete_product, list_products

urlpatterns = [
    #login path
    re_path('login',views.login),
    re_path('signup',views.signup),
    re_path('test_token',views.test_token),
    re_path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # customer paths
    path('customer/<str:customer_id>/', get_customer, name='get_customer'),
    path('customer/create/', create_customer, name='create_customer'),

    # Product paths
    path('products/', list_products, name='list_products'),

    path('products/create/', create_product, name='create_product'),
    path('products/<str:product_id>/', get_product, name='get_product'),
    path('products/<str:product_id>/update/', update_product, name='update_product'),
    path('products/<str:product_id>/delete/', delete_product, name='delete_product'),

    # Shopping Cart paths
    path('cart/<str:customer_id>/add/<str:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/<str:customer_id>/remove/<str:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/<str:customer_id>/', views.get_cart, name='get_cart'),


    # wishlist paths
    path('wishlist/<str:customer_id>/add/<str:product_id>/', add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/<str:customer_id>/remove/<str:product_id>/', remove_from_wishlist, name='remove_from_wishlist'),
    path('wishlist/<str:customer_id>/', get_wishlist, name='get_wishlist'),

    # refund paths
    path('refund/request/<int:order_item_id>/', request_refund, name='request_refund'),
    path('refund/approve/<int:refund_id>/', approve_refund, name='approve_refund'),
]


