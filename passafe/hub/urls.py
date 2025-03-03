from django.urls import path
from . import views

app_name = 'hub'

urlpatterns = [
    path('', views.HeroView.as_view(), name='hero'),
    path('dashboard/', views.homepage, name='homepage'),
]
