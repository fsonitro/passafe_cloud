import random
import string
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_protect
from django.shortcuts import render
import math

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

        # Calculate entropy in bits
        pool_size = len(characters)
        entropy_bits = round(length * math.log2(pool_size), 2)  # Using log2 for bits

        # Determine quality based on entropy in bits
        if entropy_bits < 40:
            quality = "Very Poor"
        elif entropy_bits < 60:
            quality = "Weak"
        elif entropy_bits < 80:
            quality = "Moderate"
        elif entropy_bits < 100:
            quality = "Strong"
        elif entropy_bits < 128:
            quality = "Very Strong"
        else:
            quality = "Excellent"


        # Return JSON response with generated password, entropy in bits, and quality
        return JsonResponse({
            "password": password,
            "entropy": entropy_bits,
            "quality": quality,
            "length": length
        })
    
    except ValueError as e:
        # Handle possible conversion errors for length and other parameters
        return JsonResponse({"error": "Invalid input data"}, status=400)
    except Exception as e:
        # Catch-all for any unexpected errors
        return JsonResponse({"error": str(e)}, status=500)
