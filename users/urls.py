from django.urls import path
from . import views

urlpatterns = [
    path('login/',            views.login_view,            name='login'),
    path('send-otp/',         views.send_otp_view,         name='send_otp'),
    path('verify-otp/',       views.verify_otp_view,       name='verify_otp'),
    path('logout/',           views.logout_view,           name='logout'),
    path('complete-profile/', views.complete_profile_view, name='complete_profile'),
]