from django.urls import path
from . import views

urlpatterns = [
    path('',                      views.seeker_dashboard,    name='seeker_dashboard'),
    path('recruiter/',            views.recruiter_dashboard, name='recruiter_dashboard'),
    path('post/',                 views.post_job,            name='post_job'),
    path('my-applications/',      views.my_applications,     name='my_applications'),
    path('apply/<int:job_id>/',   views.apply_to_job,        name='apply_to_job'),
]