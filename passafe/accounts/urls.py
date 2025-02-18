from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # Authentication Routes
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),

    # Account Recovery Routes
    path('forgot-password/', views.forgot_password_request, name='forgot_password_request'),
    path('verify-reset-code/', views.verify_reset_code, name='verify_reset_code'),
    path('reset-password/', views.reset_password, name='reset_password'),

    # Account Settings Routes
    path('account-settings/', views.account_settings, name='account_settings'),

    # MFA Routes
    path('enable-mfa/', views.enable_mfa, name='enable_mfa'),
    path('verify-mfa/', views.verify_mfa, name='verify_mfa'),
    path('disable-mfa/', views.disable_mfa, name='disable_mfa'),

    # Miscellaneous Routes
    path("set-theme/", views.set_theme, name="set_theme"),
    path('export-passwords/', views.export_passwords, name='export_passwords'),
    path('account-activities/', views.account_activities, name='account_activities'),


]
