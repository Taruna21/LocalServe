from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',       lambda request: redirect('login'), name='home'),
    path('',       include('users.urls')),
    path('jobs/',  include('jobs.urls')),
    path('chat/',  include('chat.urls')),
]