from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('register/', views.register, name='register'),
    path('waiting-for-approval/', views.waiting_for_approval, name='waiting_for_approval'),
    path('pending-approvals/', views.pending_approvals, name='pending_approvals'),
    path('approve-user/<int:user_id>/', views.approve_user, name='approve_user'),
    path('reject-user/<int:user_id>/', views.reject_user, name='reject_user'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('villa/add/', views.add_villa, name='add_villa'),
    path('villa/<int:villa_id>/', views.villa_detail, name='villa_detail'),
    path('villa/<int:villa_id>/payments/', views.manage_payments, name='manage_payments'),
    path('villa/<int:villa_id>/edit/', views.edit_villa, name='edit_villa'),
    path('villa/<int:villa_id>/delete/', views.delete_villa, name='delete_villa'),
    path('payment/<int:payment_id>/update/', views.update_payment, name='update_payment'),
    path('villa/<int:villa_id>/toggle_payment/', views.toggle_dashboard_payment, name='toggle_dashboard_payment'),
]
