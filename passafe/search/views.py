from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from password_vault.models import PasswordEntry

@login_required
def search_entries(request):
    query = request.GET.get('q', '').strip()
    if not query:
        return JsonResponse({'results': []})

    # Filter password entries
    results = PasswordEntry.objects.filter(user=request.user, title__icontains=query)
    
    # Format results
    data = [
        {
            'id': entry.id,
            'title': entry.title,
            'username': entry.username,
            'created_at': entry.created_at.strftime('%Y-%m-%d %H:%M'),
        }
        for entry in results
    ]
    return JsonResponse({'results': data})
