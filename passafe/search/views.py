from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from password_vault.models import PasswordEntry

@login_required
def search_entries(request):
    query = request.GET.get('q', '')
    if query:
        entries = PasswordEntry.objects.filter(
            user=request.user,
            title__icontains=query
        ).values('id', 'title', 'username')
        
        return JsonResponse({
            'results': list(entries)
        })
    return JsonResponse({'results': []})
