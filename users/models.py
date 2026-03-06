from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


class UserManager(BaseUserManager):
    def create_user(self, phone, password=None, **extra_fields):
        if not phone:
            raise ValueError('Phone number is required')
        user = self.model(phone=phone, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(phone, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [
        ('seeker',    'Job Seeker'),
        ('recruiter', 'Recruiter'),
        ('admin',     'Admin'),
    ]

    phone      = models.CharField(max_length=15, unique=True)
    email      = models.EmailField(blank=True, null=True)
    username   = models.CharField(max_length=50, blank=True, null=True, unique=True)
    full_name  = models.CharField(max_length=100, blank=True)
    role       = models.CharField(max_length=20, choices=ROLE_CHOICES, default='seeker')
    city       = models.CharField(max_length=100, blank=True)
    address    = models.TextField(blank=True)
    bio        = models.TextField(blank=True)
    skills     = models.CharField(max_length=300, blank=True)
    photo      = models.ImageField(upload_to='profile_photos/', blank=True, null=True)

    # Seeker availability
    is_available = models.BooleanField(default=True)

    otp            = models.CharField(max_length=6,  blank=True, null=True)
    otp_created_at = models.DateTimeField(blank=True, null=True)

    is_active  = models.BooleanField(default=True)
    is_staff   = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD  = 'phone'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.full_name or self.phone

    def avg_rating(self):
        ratings = self.ratings_received.all()
        if not ratings:
            return None
        return round(sum(r.stars for r in ratings) / len(ratings), 1)


class Rating(models.Model):
    rater    = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ratings_given')
    rated    = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ratings_received')
    stars    = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    review   = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['rater', 'rated']

    def __str__(self):
        return f"{self.rater} → {self.rated}: {self.stars}★"


class Notification(models.Model):
    TYPE_CHOICES = [
        ('application',   'New Application'),
        ('status_update', 'Application Status Updated'),
        ('new_job',       'New Job Posted'),
        ('message',       'New Message'),
    ]

    recipient  = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notif_type = models.CharField(max_length=30, choices=TYPE_CHOICES)
    title      = models.CharField(max_length=200)
    message    = models.TextField()
    link       = models.CharField(max_length=300, blank=True, default='')
    is_read    = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.recipient.phone} — {self.title}"
