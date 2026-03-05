from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from .models import User
from .otp_utils import generate_otp, send_otp_sms, is_otp_valid


def redirect_by_role(user):
    if user.role == 'recruiter':
        return redirect('recruiter_dashboard')
    return redirect('seeker_dashboard')


# ── LOGIN ─────────────────────────────────────────────────
def login_view(request):
    if request.user.is_authenticated:
        return redirect_by_role(request.user)

    if request.method == 'POST':
        phone    = request.POST.get('phone', '').strip()
        password = request.POST.get('password', '').strip()

        if not phone or not password:
            messages.error(request, 'Please enter both phone and password.')
            return render(request, 'users/login.html', {'phone': phone})

        user = authenticate(request, username=phone, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.full_name or user.phone}!')
            return redirect_by_role(user)
        else:
            messages.error(request, 'Invalid phone number or password.')
            return render(request, 'users/login.html', {'phone': phone})

    return render(request, 'users/login.html')


# ── SIGNUP ────────────────────────────────────────────────
def signup_view(request):
    if request.user.is_authenticated:
        return redirect_by_role(request.user)
    return render(request, 'users/signup.html')


def send_otp_view(request):
    if request.method != 'POST':
        return redirect('signup')

    phone  = request.POST.get('phone', '').strip()
    intent = request.POST.get('intent', 'seeker')

    if not phone or len(phone) != 10 or not phone.isdigit():
        messages.error(request, 'Enter a valid 10-digit mobile number.')
        return render(request, 'users/signup.html', {'phone': phone, 'intent': intent})

    # Get or create user — allow re-signup if no password set yet
    user, created = User.objects.get_or_create(phone=phone)

    # If user already has a password they are registered — send to login
    if not created and user.has_usable_password():
        messages.error(request, 'This number is already registered. Please login.')
        return redirect('login')

    otp = generate_otp()
    user.otp            = otp
    user.otp_created_at = timezone.now()
    user.save()

    send_otp_sms(phone, otp)

    return render(request, 'users/signup.html', {
        'otp_sent': True,
        'phone':    phone,
        'intent':   intent,
    })


def verify_otp_view(request):
    if request.method != 'POST':
        return redirect('signup')

    phone  = request.POST.get('phone', '').strip()
    otp    = request.POST.get('otp', '').strip()
    intent = request.POST.get('intent', 'seeker')

    try:
        user = User.objects.get(phone=phone)
    except User.DoesNotExist:
        messages.error(request, 'Phone not found. Please try again.')
        return redirect('signup')

    valid, message = is_otp_valid(user, otp)

    if not valid:
        messages.error(request, message)
        return render(request, 'users/signup.html', {
            'otp_sent': True,
            'phone':    phone,
            'intent':   intent,
        })

    user.otp            = None
    user.otp_created_at = None
    user.save()

    login(request, user)
    request.session['intent'] = intent
    return redirect('complete_profile')


# ── COMPLETE PROFILE ──────────────────────────────────────
@login_required
def complete_profile_view(request):
    if request.method == 'POST':
        user           = request.user
        user.full_name = request.POST.get('full_name', '').strip()
        user.role      = request.POST.get('role', 'seeker')
        user.city      = request.POST.get('city', '').strip()
        user.address   = request.POST.get('address', '').strip()

        password  = request.POST.get('password', '').strip()
        password2 = request.POST.get('password2', '').strip()

        if not password or len(password) < 6:
            messages.error(request, 'Password must be at least 6 characters.')
            return render(request, 'users/complete_profile.html', {
                'intent': request.session.get('intent', 'seeker')
            })

        if password != password2:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'users/complete_profile.html', {
                'intent': request.session.get('intent', 'seeker')
            })

        user.set_password(password)
        user.save()

        login(request, user)
        messages.success(request, f'Welcome to KaamMilao, {user.full_name}! 🎉')
        return redirect_by_role(user)

    intent = request.session.get('intent', 'seeker')
    return render(request, 'users/complete_profile.html', {'intent': intent})


# ── LOGOUT ────────────────────────────────────────────────
def logout_view(request):
    logout(request)
    messages.info(request, 'Logged out successfully.')
    return redirect('login')


# ── NOTIFICATIONS ─────────────────────────────────────────
@login_required
def notifications_view(request):
    from .models import Notification
    notifs = Notification.objects.filter(recipient=request.user)
    notifs.filter(is_read=False).update(is_read=True)
    return render(request, 'users/notifications.html', {'notifications': notifs})
