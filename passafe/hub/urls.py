from django.urls import path
from . import views

# Define the application namespace for URL reversing
app_name = 'hub'

# URL patterns for the hub application
urlpatterns = [
    # Landing page/Hero view for unauthenticated users
    path('', views.HeroView.as_view(), name='hero'),
    
    # Main dashboard view for authenticated users
    path('dashboard/', views.homepage, name='homepage'),
]
