from django.urls import path
from .views import *

urlpatterns = [
    # Email registration
    # path('register/email/', EmailRegisterAPIView.as_view(), name='register-email'),
    path('resend/otp/', ResendOTPAPIView.as_view(), name='resend-otp'),
    # Verify OTP
    path('verify/otp/', VerifyOTPAPIView.as_view(), name='verify-otp'),
    # Phone registration - generate OTP
    path('register/phone/', PhoneRegisterAPIView.as_view(), name='register-phone'),

    # Login
    # path('login/', LoginAPIView.as_view(), name='login'),
    # path('reset-password-link/', ResetPasswordLinkAPIView.as_view(), name='reset-password-link'),
    # path('reset-password/<str:token>/', ResetPasswordAPIView.as_view(), name='reset-password'),
]
