from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from rest_framework import generics, permissions, filters
from rest_framework.response import Response

from .models import Job
from .serializers import JobSerializer, JobCreateSerializer
from applications.models import Application


# ─────────────────────────────────────────────
# TEMPLATE VIEWS
# ─────────────────────────────────────────────

@login_required
def seeker_dashboard(request):
    jobs     = Job.objects.filter(status='open')  # ← removed select_related
    city     = request.GET.get('city', '').strip()
    category = request.GET.get('category', '')

    if city:     jobs = jobs.filter(city__icontains=city)
    if category: jobs = jobs.filter(category=category)

    applied_job_ids = list(
        Application.objects.filter(applicant=request.user).values_list('job_id', flat=True)
    )

    my_applications = Application.objects.filter(
        applicant=request.user
    ).select_related('job').order_by('-applied_at')

    return render(request, 'jobs/seeker_dashboard.html', {
        'jobs':            jobs,
        'city':            city,
        'category':        category,
        'applied_job_ids': applied_job_ids,
        'my_applications': my_applications,
        'categories':      Job.CATEGORY_CHOICES,
    })

@login_required
def recruiter_dashboard(request):
    jobs = Job.objects.filter(posted_by=request.user).order_by('-created_at')
    return render(request, 'jobs/recruiter_dashboard.html', {'jobs': jobs})


@login_required
def post_job(request):
    if request.method == 'POST':
        Job.objects.create(
            posted_by   = request.user,
            title       = request.POST.get('title'),
            category    = request.POST.get('category'),
            description = request.POST.get('description', ''),
            city        = request.POST.get('city'),
            area        = request.POST.get('area', ''),
            pay_amount  = request.POST.get('pay_amount'),
            pay_type    = request.POST.get('pay_type'),
        )
        messages.success(request, 'Job posted successfully!')
        return redirect('recruiter_dashboard')
    return render(request, 'jobs/post_job.html', {
        'categories': Job.CATEGORY_CHOICES,
    })


@login_required
def my_applications(request):
    apps = Application.objects.filter(
        applicant=request.user
    ).select_related('job').order_by('-applied_at')
    return render(request, 'jobs/my_applications.html', {'applications': apps})


@login_required
def apply_to_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    _, created = Application.objects.get_or_create(job=job, applicant=request.user)
    if created:
        messages.success(request, f'Applied to "{job.title}" successfully!')
    else:
        messages.info(request, 'You already applied to this job.')
    return redirect('seeker_dashboard')


# ─────────────────────────────────────────────
# API VIEWS (for Postman / future mobile app)
# ─────────────────────────────────────────────

class JobListView(generics.ListAPIView):
    serializer_class   = JobSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends    = [filters.SearchFilter]
    search_fields      = ['title', 'city', 'area', 'category']

    def get_queryset(self):
        queryset = Job.objects.filter(status='open')
        city     = self.request.query_params.get('city')
        category = self.request.query_params.get('category')
        if city:     queryset = queryset.filter(city__icontains=city)
        if category: queryset = queryset.filter(category=category)
        return queryset


class JobCreateView(generics.CreateAPIView):
    serializer_class   = JobCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(posted_by=self.request.user)


class JobDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class   = JobSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return Job.objects.all()

    def update(self, request, *args, **kwargs):
        job = self.get_object()
        if job.posted_by != request.user:
            return Response({'error': 'You can only edit your own jobs'}, status=403)
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        job = self.get_object()
        if job.posted_by != request.user:
            return Response({'error': 'You can only delete your own jobs'}, status=403)
        return super().destroy(request, *args, **kwargs)


class MyJobsView(generics.ListAPIView):
    serializer_class   = JobSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Job.objects.filter(posted_by=self.request.user)