from django.contrib import admin
from django.urls import path, include  # include is necessary to include app urls

urlpatterns = [
    path('admin/', admin.site.urls),
    path('shoesite/', include('shoesite.urls')),  # Include the app URLs
]
