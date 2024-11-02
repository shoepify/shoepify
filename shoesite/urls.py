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

from django.contrib import admin
from django.urls import path
from . import views
from .views import get_customer, create_customer, request_refund, approve_refund

urlpatterns = [
    path('customer/<int:customer_id>/', get_customer, name='get_customer'),
    path('customer/create/', create_customer, name='create_customer'),

    # refund processes
    path('request-refund/<int:order_item_id>/', views.request_refund, name='request_refund'),
    path('approve-refund/<int:refund_id>/', views.approve_refund, name='approve_refund'),
]
