import json
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_protect
from django.shortcuts import render

@csrf_protect
@require_POST
def generate_password(request):
    try:
        # Get the options from the POST request
        options = {
            'length': int(request.POST.get('length', 12)),
            'includeUppercase': request.POST.get('include_uppercase') == 'true',
            'includeLowercase': request.POST.get('include_lowercase') == 'true',
            'includeNumbers': request.POST.get('include_numbers') == 'true',
            'includeSymbols': request.POST.get('include_symbols') == 'true'
        }

        # Return the options for client-side generation
        return JsonResponse({
            'success': True,
            'options': options
        })
    except ValueError as e:
        return JsonResponse({'error': 'Invalid input parameters'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
