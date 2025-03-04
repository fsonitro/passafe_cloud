import json
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_protect
from django.shortcuts import render

@csrf_protect  # Ensure CSRF protection for security
@require_POST  # Only allow POST requests to this view
def generate_password(request):
    """
    API endpoint to handle password generation requests.
    Returns password generation options as JSON for client-side generation.
    This approach prevents sensitive password data from being transmitted over the network.
    """
    try:
        # Parse and validate password generation options from POST data
        options = {
            'length': int(request.POST.get('length', 12)),  # Default length: 12
            'includeUppercase': request.POST.get('include_uppercase') == 'true',
            'includeLowercase': request.POST.get('include_lowercase') == 'true',
            'includeNumbers': request.POST.get('include_numbers') == 'true',
            'includeSymbols': request.POST.get('include_symbols') == 'true'
        }

        # Return validated options for client-side password generation
        return JsonResponse({
            'success': True,
            'options': options
        })
    except ValueError as e:
        # Handle invalid input parameters (e.g., non-integer length)
        return JsonResponse({'error': 'Invalid input parameters'}, status=400)
    except Exception as e:
        # Handle unexpected errors
        return JsonResponse({'error': str(e)}, status=500)
