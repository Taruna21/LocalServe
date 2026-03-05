from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, logout
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from .models import User
from .otp_utils import generate_otp, send_otp_sms, is_otp_valid


def login_view(request):
    # Already logged in → redirect to dashboard
    if request.user.is_authenticated:
        return redirect_by_role(request.user)
    return render(request, 'users/login.html')


def send_otp_view(request):
    if request.method != 'POST':
        return redirect('login')

    phone  = request.POST.get('phone', '').strip()
    intent = request.POST.get('intent', 'seeker')   # ← from signup form

    if not phone or len(phone) != 10 or not phone.isdigit():
        messages.error(request, 'Enter a valid 10-digit mobile number')
        return redirect('login')

    user, created = User.objects.get_or_create(phone=phone)
    otp = generate_otp()
    user.otp = otp
    user.otp_created_at = timezone.now()
    user.save()

    send_otp_sms(phone, otp)

    return render(request, 'users/login.html', {
        'otp_sent': True,
        'phone':    phone,
        'intent':   intent,    # ← pass intent to OTP step
    })


def verify_otp_view(request):
    if request.method != 'POST':
        return redirect('login')

    phone  = request.POST.get('phone', '').strip()
    otp    = request.POST.get('otp', '').strip()
    intent = request.POST.get('intent', 'seeker')

    try:
        user = User.objects.get(phone=phone)
    except User.DoesNotExist:
        messages.error(request, 'Phone not found. Please try again.')
        return redirect('login')

    valid, message = is_otp_valid(user, otp)

    if not valid:
        messages.error(request, message)
        return render(request, 'users/login.html', {
            'otp_sent': True,
            'phone':    phone,
            'intent':   intent,
        })

    user.otp = None
    user.otp_created_at = None
    user.save()

    login(request, user)

    # New user → set their intent as role hint and send to profile
    if not user.full_name:
        request.session['intent'] = intent
        return redirect('complete_profile')

    return redirect_by_role(user)


def logout_view(request):
    logout(request)
    messages.info(request, 'Logged out successfully.')
    return redirect('login')


@login_required
def complete_profile_view(request):
    if request.method == 'POST':
        user           = request.user
        user.full_name = request.POST.get('full_name', '').strip()
        user.role      = request.POST.get('role', 'seeker')
        user.city      = request.POST.get('city', '').strip()
        user.address   = request.POST.get('address', '').strip()
        user.save()
        messages.success(request, 'Profile saved!')
        return redirect_by_role(user)

    # Pre-select role from signup intent
    intent = request.session.get('intent', 'seeker')
    return render(request, 'users/complete_profile.html', {'intent': intent})


def redirect_by_role(user):
    if user.role == 'recruiter':
        return redirect('recruiter_dashboard')
    return redirect('seeker_dashboard')