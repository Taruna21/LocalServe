from django.db import models
from users.models import User
from jobs.models import Job


class Application(models.Model):

    STATUS_CHOICES = [
        ('pending',     'Pending'),
        ('shortlisted', 'Shortlisted'),
        ('rejected',    'Rejected'),
        ('hired',       'Hired'),
    ]

    job       = models.ForeignKey(Job,  on_delete=models.CASCADE, related_name='applications')
    applicant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='my_applications')

    applicant_name  = models.CharField(max_length=100, default='')
    applicant_phone = models.CharField(max_length=15,  default='')
    applicant_city  = models.CharField(max_length=100, blank=True, default='')
    cover_note      = models.TextField(blank=True, default='')

    status     = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-applied_at']
        unique_together = ['job', 'applicant']

    def __str__(self):
        return f"{self.applicant_name} → {self.job.title} ({self.status})"
