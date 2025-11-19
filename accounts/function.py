import random
from datetime import timedelta
from django.utils import timezone
from .models import OTP, User

# def generate_otp_for_user(phone):
#     otp_code = str(random.randint(1000, 9999))

#     # Get or create user
#     user, created = User.objects.get_or_create(phone=phone)

#     # Create OTP entry
#     otp = OTP.objects.create(
#         user=user,
#         otp_code=otp_code,
#         otp_type='phone',
#         expires_at=timezone.now() + timedelta(minutes=5)
#     )

#     # Send OTP via SMS service or print to console
#     print(f"OTP for {phone}: {otp_code}")

#     # Return both OTP and user
#     return otp, user


def generate_otp_for_user(phone, length=6, ttl_minutes=5):
    # generate zero-padded 6-digit code
    start = 10**(length-1)
    end = (10**length) - 1
    otp_code = str(random.randint(start, end))

    otp = OTP.objects.create(
        user=None,          # don't create or attach user
        phone=phone,
        otp_code=otp_code,
        otp_type='phone',
        expires_at=timezone.now() + timedelta(minutes=ttl_minutes)
    )

    # send via SMS provider here (or print for dev)
    print(f"OTP for {phone}: {otp_code}")

    return otp



def verify_otp(phone, otp_code):
    # Get the latest unused OTP for this phone number
    otp = OTP.objects.filter(
        phone=phone,
        otp_type='phone',
        otp_code=otp_code,
        is_used=False
    ).order_by('-created_at').first()

    # Invalid OTP
    if not otp:
        return False, "Invalid OTP"

    # Expired OTP
    if otp.expires_at < timezone.now():
        return False, "OTP Expired"

    # Mark OTP as used
    otp.is_used = True
    otp.save(update_fields=['is_used'])

    # Return success
    return True, "OTP Verified Successfully"