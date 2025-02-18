from django.urls import path
from . import views

app_name = 'password_generator'

urlpatterns = [
    # path('form/', views.generator_form, name='generator_form'),
    path('generate/', views.generate_password, name='generate_password'),
]
