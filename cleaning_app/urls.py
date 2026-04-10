from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('villa/add/', views.add_villa, name='add_villa'),
    path('villa/<int:villa_id>/', views.villa_detail, name='villa_detail'),
    path('villa/<int:villa_id>/payments/', views.manage_payments, name='manage_payments'),
    path('payment/<int:payment_id>/update/', views.update_payment, name='update_payment'),
    path('villa/<int:villa_id>/toggle_payment/', views.toggle_dashboard_payment, name='toggle_dashboard_payment'),
]
