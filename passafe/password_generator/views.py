import random
import string
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_protect
from django.shortcuts import render

@csrf_protect  # Enable CSRF protection for security
@require_POST
def generate_password(request):
    try:
        # Fetch password criteria from POST request
        length = int(request.POST.get('length', 12))  # Default length is 12
        include_uppercase = request.POST.get('include_uppercase', 'true') == 'true'
        include_lowercase = request.POST.get('include_lowercase', 'true') == 'true'
        include_numbers = request.POST.get('include_numbers', 'true') == 'true'
        include_symbols = request.POST.get('include_symbols', 'false') == 'true'

        # Character pools based on user input
        characters = ""
        if include_uppercase:
            characters += string.ascii_uppercase
        if include_lowercase:
            characters += string.ascii_lowercase
        if include_numbers:
            characters += string.digits
        if include_symbols:
            characters += "!@#$%^&*()-_=+[]{}|;:,.<>?/~`"

        # Error response if no character type selected
        if not characters:
            return JsonResponse({"error": "No character types selected"}, status=400)
        
        # Generate password from selected characters
        password = ''.join(random.choice(characters) for _ in range(length))

        # Return JSON response with generated password and length
        return JsonResponse({
            "password": password,
            "length": length
        })
    
    except ValueError:
        # Handle possible conversion errors for length and other parameters
        return JsonResponse({"error": "Invalid input data"}, status=400)
    except Exception as e:
        # Catch-all for any unexpected errors
        return JsonResponse({"error": str(e)}, status=500)
