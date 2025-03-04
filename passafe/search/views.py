from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from password_vault.models import PasswordEntry

@login_required  # Ensure only authenticated users can search
def search_entries(request):
    """
    AJAX endpoint for searching password entries.
    Performs case-insensitive search on entry titles for the authenticated user.
    
    Parameters:
        request: HTTP request object containing 'q' parameter for search query
    
    Returns:
        JsonResponse containing matching password entries with id, title, and username
        Returns empty results if no query provided or no matches found
    
    Security:
        - Only returns entries belonging to the authenticated user
        - Does not expose sensitive password data
        - Protected by login_required decorator
    """
    query = request.GET.get('q', '')
    if query:
        # Search for entries matching the query, limited to user's own entries
        entries = PasswordEntry.objects.filter(
            user=request.user,
            title__icontains=query
        ).values('id', 'title', 'username')
        
        return JsonResponse({
            'results': list(entries)
        })
    return JsonResponse({'results': []})  # Return empty results if no query
