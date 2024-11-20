from django.shortcuts import render, redirect
from django.http import JsonResponse
from ..models import Guest

def home_view(request):
    
    """
    Handle the root URL and manage guest users without template
    Just creates guest user and can redirect to your main page or return guest info
    """
    # Create or get guest user
    if not request.session.session_key:
        request.session.create()
    
    session_id = request.session.session_key
    
    # Try to get existing guest user
    guest, created = Guest.objects.get_or_create(
        session_id=session_id,
        defaults={
            'session_id': session_id
        }
    )
    
    # Store guest_id in session
    request.session['guest_id'] = guest.guest_id

    # Option 1: Return JSON response with guest info
    return JsonResponse({
        'guest_id': guest.guest_id,
        'session_id': guest.session_id,
        'created_at': guest.created_at.isoformat()
    })

    # Option 2: Redirect to your main page
    # return redirect('your-main-page')  # Uncomment this and comment out JsonResponse if you want to redirect

# Middleware remains the same
class GuestUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.user.is_authenticated:
            if not request.session.session_key:
                request.session.create()
            
            session_id = request.session.session_key
            guest, created = Guest.objects.get_or_create(
                session_id=session_id,
                defaults={
                    'session_id': session_id
                }
            )
            request.guest = guest
        
        response = self.get_response(request)
        return response