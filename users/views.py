from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone

from .models import User
from .otp_utils import generate_otp, send_otp_sms, is_otp_valid


def get_tokens_for_user(user):
    """Generate JWT access + refresh tokens for a user."""
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access':  str(refresh.access_token),
    }


class SendOTPView(APIView):
    """
    POST /api/auth/send-otp/
    Body: { "phone": "9876543210" }

    Creates user if doesn't exist, sends OTP via SMS.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        phone = request.data.get('phone', '').strip()

        if not phone or len(phone) != 10:
            return Response(
                {'error': 'Enter a valid 10-digit phone number'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get or create user with this phone
        user, created = User.objects.get_or_create(phone=phone)

        # Generate OTP and save to DB
        otp = generate_otp()
        user.otp            = otp
        user.otp_created_at = timezone.now()
        user.save()

        # Send SMS
        sent = send_otp_sms(phone, otp)

        if sent:
            return Response({
                'message': f'OTP sent to {phone}',
                'new_user': created   # frontend can show profile setup if True
            })
        else:
            return Response(
                {'error': 'Failed to send OTP. Try again.'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )


class VerifyOTPView(APIView):
    """
    POST /api/auth/verify-otp/
    Body: { "phone": "9876543210", "otp": "847291" }

    Verifies OTP, returns JWT tokens on success.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        phone = request.data.get('phone', '').strip()
        otp   = request.data.get('otp', '').strip()

        try:
            user = User.objects.get(phone=phone)
        except User.DoesNotExist:
            return Response(
                {'error': 'Phone number not found. Please request OTP first.'},
                status=status.HTTP_404_NOT_FOUND
            )

        valid, message = is_otp_valid(user, otp)

        if not valid:
            return Response(
                {'error': message},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Clear OTP after successful verification (security)
        user.otp            = None
        user.otp_created_at = None
        user.save()

        tokens = get_tokens_for_user(user)

        return Response({
            'message': 'Login successful',
            'tokens':  tokens,
            'user': {
                'id':        user.id,
                'phone':     user.phone,
                'full_name': user.full_name,
                'role':      user.role,
                'city':      user.city,
            }
        })


class CompleteProfileView(APIView):
    """
    POST /api/auth/complete-profile/
    New users fill in their name, role, city after first login.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        user.full_name = request.data.get('full_name', user.full_name)
        user.role      = request.data.get('role', user.role)
        user.city      = request.data.get('city', user.city)
        user.address   = request.data.get('address', user.address)
        user.email     = request.data.get('email', user.email)
        user.save()

        return Response({
            'message': 'Profile updated',
            'user': {
                'id':        user.id,
                'phone':     user.phone,
                'full_name': user.full_name,
                'role':      user.role,
                'city':      user.city,
            }
        })