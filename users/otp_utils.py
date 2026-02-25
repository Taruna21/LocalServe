import random
import requests
from django.conf import settings
from django.utils import timezone


def generate_otp():
    return str(random.randint(100000, 999999))


def send_otp_sms(phone, otp):
    # DEV MODE - OTP prints in terminal instead of SMS
    print(f"\n{'='*40}")
    print(f"  OTP for {phone} is: {otp}")
    print(f"{'='*40}\n")
    return True

    # PRODUCTION - uncomment when Fast2SMS is ready
    # url = "https://www.fast2sms.com/dev/bulkV2"
    # payload = {
    #     "route":            "otp",
    #     "variables_values": otp,
    #     "numbers":          phone,
    # }
    # headers = {
    #     "authorization": settings.FAST2SMS_API_KEY,
    #     "Content-Type":  "application/json",
    # }
    # try:
    #     response = requests.post(url, json=payload, headers=headers)
    #     data = response.json()
    #     print("Fast2SMS response:", data)
    #     return data.get('return', False)
    # except Exception as e:
    #     print(f"SMS error: {e}")
    #     return False


def is_otp_valid(user, otp_entered):
    if user.otp != otp_entered:
        return False, "Invalid OTP"

    time_diff = timezone.now() - user.otp_created_at
    if time_diff.seconds > 1800:   # 30 minutes
        return False, "OTP expired. Please request a new one."

    return True, "Valid"