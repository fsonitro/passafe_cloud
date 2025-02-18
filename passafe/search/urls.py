from django.urls import path
from . import views

app_name = 'search'

urlpatterns = [
    path('entries/', views.search_entries, name='search_entries'),
]
