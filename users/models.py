from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager, PermissionsMixin


class UserManager(BaseUserManager):
    def create_user(self, phone, password=None, **extra_fields):
        if not phone:
            raise ValueError('phone number is required')
        user = self.model(phone=phone, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, phone, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self.create_user(phone, password, **extra_fields)

class User(AbstractUser, PermissionsMixin):
    username = None
    ROLE_CHOICES = [
        ('seeker', 'Job Seeker'),
        ('recruiter', 'Recruiter'),
        ('admin', 'Admin')
    ]

    phone = models.CharField(max_length=15, unique=True)
    email = models.EmailField(blank=True, null=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='seeker')

    full_name = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    address = models.TextField(max_length=100,blank=True)

    otp = models.CharField(max_length=6, blank=True, null=True)
    otp_created_at = models.DateTimeField(blank=True, null=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = []

    def __str__(self):
        return f"{self.phone} ({self.role})"