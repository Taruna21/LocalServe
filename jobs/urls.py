from django.urls import path
from . import views

urlpatterns = [
    # Seeker
    path('',                          views.seeker_dashboard,           name='seeker_dashboard'),
    path('apply/<int:job_id>/',       views.apply_to_job,               name='apply_to_job'),
    path('my-applications/',          views.my_applications,            name='my_applications'),

    # Recruiter
    path('recruiter/',                views.recruiter_dashboard,        name='recruiter_dashboard'),
    path('recruiter/post/',           views.post_job,                   name='post_job'),
    path('recruiter/applicants/<int:job_id>/',   views.job_applicants,  name='job_applicants'),
    path('recruiter/delete/<int:job_id>/',       views.delete_job,      name='delete_job'),
    path('recruiter/application/<int:app_id>/status/', views.update_application_status, name='update_application_status'),

    # API
    path('api/',          views.JobListView.as_view(),   name='job-list'),
    path('api/create/',   views.JobCreateView.as_view(), name='job-create'),
    path('api/<int:pk>/', views.JobDetailView.as_view(), name='job-detail'),
    path('api/mine/',     views.MyJobsView.as_view(),    name='my-jobs'),
]