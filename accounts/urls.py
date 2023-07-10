from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('', views.dashboard, name='dashboard'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    path('forgotpassword/', views.forgotpassword, name='forgotpassword'),
    path('resetpassword_validate/<uidb64>/<token>/', views.resetpassword_validate, name='resetpassword_validate'),
    path('resetpassword/', views.resetpassword, name='resetpassword'),

    path('my_orders/', views.my_orders, name='my_orders'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('charge_password/', views.charge_password, name='charge_password'),
    path('order_detail/<int:order_id>/', views.order_detail, name='order_detail'),

    path('contactus/', views.contact, name='contact_us'),
    path('aboutus/', views.aboutus, name='aboutust_us'),
]

