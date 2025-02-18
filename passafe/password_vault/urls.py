from django.urls import path
from . import views

app_name = 'password_vault'

urlpatterns = [
    # Dashboard
    path('dashboard/', views.vault_dashboard, name='vault_dashboard'),
    
    # Folder management
    path('folders/create/', views.create_folder, name='create_folder'),
    path('folders/<int:folder_id>/edit/', views.edit_folder, name='edit_folder'),
    path('folders/<int:folder_id>/delete/', views.delete_folder, name='delete_folder'),
    path("folder_entries/<int:folder_id>/", views.folder_entries, name="folder_entries"),

    # Password entry management
    path('entries/create/', views.create_entry_no_folder, name='create_entry_no_folder'),
    path('folders/<int:folder_id>/entries/create/', views.create_entry, name='create_entry'),
    path('entries/<int:entry_id>/edit/', views.edit_entry, name='edit_entry'),
    path('entries/<int:entry_id>/delete/', views.delete_entry, name='delete_entry'),

    # View password entry in the vault dashboard
    path('view_password/<int:entry_id>/', views.view_password, name='view_password'),

]
