from django.urls import path
from . import views

app_name = 'admin_dashboard'

urlpatterns = [
    path('login/', views.admin_login, name='login'),
    path('logout/', views.admin_logout, name='logout'),
    path('', views.admin_dashboard, name='dashboard'),
    # Console log APIs
    path('api/commands/', views.api_commands, name='api_commands'),
    path('api/logs/', views.api_logs, name='api_logs'),
    path('api/run-script/', views.api_run_script, name='api_run_script'),
    # Data insertion APIs
    path('api/tables/', views.api_tables, name='api_tables'),
    path('api/tables/<str:table_name>/columns/', views.api_table_columns, name='api_table_columns'),
    path('api/insert/', views.api_insert, name='api_insert'),
    # User management APIs
    path('api/users/', views.api_users_list, name='api_users_list'),
    path('api/users/<int:user_id>/', views.api_user_detail, name='api_user_detail'),
]
