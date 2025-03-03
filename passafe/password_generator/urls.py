from django.urls import path
from . import views

app_name = 'password_generator'

urlpatterns = [
    path('generate/', views.generate_password, name='generate_password'),
]
