from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics, status
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import (
    EmailRegisterSerializer,
    PhoneRegisterSerializer,
    OTPVerifySerializer,
    LoginSerializer,
    ResendOtpSerializer,
    PasswordRetypeSerializer,
    PasswordSerializer,

)
from .models import User, UserProfile
from .function import generate_otp_for_user, verify_otp
from django.contrib.sites.shortcuts import get_current_site
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework.authtoken.models import Token
from django.core.mail import send_mail
from lokayukta.emails import *
import urllib.parse
from rest_framework.permissions import AllowAny
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.authtoken.models import Token
from django.db import transaction


# # -------------------------------
# # Email Registration
# # -------------------------------
# class EmailRegisterAPIView(generics.GenericAPIView):
#     serializer_class = EmailRegisterSerializer

#     def post(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)

#         data = serializer.validated_data
#         email = data.get('email')
#         user_source = data.get('user_source', None)
#         password = data.get('password')

#         # User create
#         user, created = User.objects.get_or_create(email=email)
#         if password:
#             user.set_password(password)
#             user.save()

#         # Optional: Update only user_source in profile
#         if user_source:
#             UserProfile.objects.update_or_create(user=user, defaults={'user_source': user_source})

#         # JWT Token
#         refresh = RefreshToken.for_user(user)
#         return Response({
#             "refresh": str(refresh),
#             "access": str(refresh.access_token),
#             "detail": "User registered successfully via email"
#         }, status=status.HTTP_201_CREATED)

# -------------------------------
# Phone Registration
# -------------------------------
class PhoneRegisterAPIView(generics.GenericAPIView):
    serializer_class = PhoneRegisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        phone = data.get('phone')
        email = data.get('email') or None
        full_name = data.get('full_name')
        father_name = data.get('father_name')
        date_of_birth = data.get('date_of_birth')
        gender = data.get('gender')
        user_source = data.get('user_source', None)

        if User.objects.filter(phone=phone).exists():
            return Response(
                {"message": "Phone number already registered. Please login instead."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Start atomic transaction
            with transaction.atomic():
                user = User.objects.create(phone=phone, email=email)
                profile = UserProfile.objects.create(
                    user=user,
                    full_name=full_name,
                    father_name=father_name,
                    date_of_birth=date_of_birth,
                    gender=gender,
                    user_source=user_source
                )

                refresh = RefreshToken.for_user(user)

            #  If we reach here, both inserts succeeded — commit transaction
            return Response(
                data={
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                    "data": {
                        "id": user.id,
                        "email": user.email,
                        "phone": user.phone,
                        "full_name": profile.full_name,
                        "father_name": profile.father_name,
                        "date_of_birth": profile.date_of_birth,
                        "gender": profile.gender,
                        "user_source": profile.user_source,
                    },
                    "login": True,
                    "message": "User registered successfully."
                },
                status=status.HTTP_201_CREATED
            )

        except Exception as e:
            # Any failure will automatically roll back due to atomic()
            return Response(
                {"message": f"User registration failed: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        


class VerifyOTPAPIView(generics.GenericAPIView):
    serializer_class = OTPVerifySerializer
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone = serializer.validated_data['phone']
        otp_code = serializer.validated_data['otp_code']

        success, message = verify_otp(phone, otp_code)
        if not success:
            return Response({"data": message}, status=status.HTTP_400_BAD_REQUEST)

        #  Get user if exists
        user = User.objects.filter(phone=phone).first()
        if not user:
            return Response(
                data = {
                    "data": {},
                    "login": False,
                    "message": "Phone verified successfully, but no user found. Please proceed with registration."
                    },
                status=status.HTTP_200_OK
            )

        # Create profile if not exists
        profile, _ = UserProfile.objects.get_or_create(user=user)

        # Generate tokens
        refresh = RefreshToken.for_user(user)
        return Response(
            data={
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "data": {
                    "id": user.id,
                    "email": user.email,
                    "phone": user.phone,
                    "user_source": profile.user_source,
                },
                "login": True,
                "message": "OTP verified successfully and user logged in"
            },
            status=status.HTTP_200_OK
        )

    

class ResendOTPAPIView(generics.GenericAPIView):
    serializer_class = ResendOtpSerializer  # सिर्फ phone चाहिए resend के लिए

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone = serializer.validated_data.get('phone')

        # try:
        #     user = User.objects.get(phone=phone)
        # except User.DoesNotExist:
        #     return Response(
        #         {"detail": "User with this phone does not exist."},
        #         status=status.HTTP_404_NOT_FOUND
        #     )

        # Generate new OTP
        otp = generate_otp_for_user(phone)
        print("otp code ",otp)
        return Response(
                data = {
                    "data": {
                        "phone": phone,
                        "otp_code": otp.otp_code
                        },
                        "message": f"OTP resent to {phone}"
                        },
                status=status.HTTP_200_OK
            )
    


# -------------------------------
# Login API
# -------------------------------
# class LoginAPIView(generics.GenericAPIView):
#     serializer_class = LoginSerializer

#     def post(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)

#         email = serializer.validated_data['email']
#         password = serializer.validated_data.get('password', None)

#         user = authenticate(request, email=email, password=password)
#         if not user:
#             return Response({"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

#         # JWT Token
#         refresh = RefreshToken.for_user(user)

#         # Ensure profile exists
#         profile, _ = UserProfile.objects.get_or_create(user=user)

#         return Response(
#             data={
#                 "refresh": str(refresh),
#                 "access": str(refresh.access_token),
#                 "data": {
#                     "id": user.id,
#                     "email": user.email,
#                     "phone": user.phone if user.phone else None,
#                     "user_source": profile.user_source if profile.user_source else None,
#                 },
#                 "message": "Login successful"
#             },
#             status=status.HTTP_200_OK
#         )






# -------------------------------
# Reset Password Link
# -------------------------------
# class ResetPasswordLinkAPIView(generics.GenericAPIView):
#     permission_classes = [AllowAny]

#     @swagger_auto_schema(
#         request_body=openapi.Schema(
#             type=openapi.TYPE_OBJECT,
#             properties={
#                 'email': openapi.Schema(type=openapi.TYPE_STRING, description='User email')
#             },
#             required=['email']
#         ),
#         responses={
#             200: openapi.Response('Token Generated Successfully'),
#             400: 'Bad Request',
#             404: 'User not found'
#         }
#     )
#     def post(self, request, *args, **kwargs):
#         email = request.data.get("email")
#         if not email:
#             return Response({"email": "This field is required."}, status=status.HTTP_400_BAD_REQUEST)
#         try:
#             user = User.objects.get(email=email, is_active=True)
#         except User.DoesNotExist:
#             return Response({"email": "User with this email does not exist."}, status=status.HTTP_404_NOT_FOUND)

#         token, created = Token.objects.get_or_create(user=user)
#         current_site = get_current_site(request).domain
#         token_url = f"http://{current_site}/reset-password/{token.key}"
#         forgot_password_send_email({'link': token_url}, [email])

#         return Response({"status": "Token Generated Successfully"}, status=status.HTTP_200_OK)

# -------------------------------
# Reset Password Using Token
# -------------------------------
# class ResetPasswordAPIView(generics.GenericAPIView):
#     permission_classes = [AllowAny]

#     @swagger_auto_schema(
#         manual_parameters=[
#             openapi.Parameter('token', openapi.IN_PATH, description="Reset Token", type=openapi.TYPE_STRING)
#         ],
#         responses={
#             200: 'Token Validated',
#             400: 'Invalid Token'
#         }
#     )
#     def get(self, request, token, *args, **kwargs):
#         try:
#             Token.objects.get(key=token)
#             return Response({"status": "Token Validated"}, status=status.HTTP_200_OK)
#         except Token.DoesNotExist:
#             return Response({"non_field_errors": "Invalid Token!"}, status=status.HTTP_400_BAD_REQUEST)

#     @swagger_auto_schema(
#         manual_parameters=[
#             openapi.Parameter('token', openapi.IN_PATH, description="Reset Token", type=openapi.TYPE_STRING)
#         ],
#         request_body=PasswordRetypeSerializer,
#         responses={200: 'Password reset successfully', 400: 'Invalid Token / validation errors'}
#     )
#     def post(self, request, token, *args, **kwargs):
#         data = request.data
#         try:
#             token_obj = Token.objects.get(key=token)
#             user = token_obj.user
#         except Token.DoesNotExist:
#             return Response({"non_field_errors": "Invalid Token!"}, status=status.HTTP_400_BAD_REQUEST)

#         serializer = PasswordRetypeSerializer(data=data, context={"user": user})
#         if serializer.is_valid():
#             new_password = serializer.validated_data.get('new_password')
#             user.set_password(new_password)
#             user.save()
#             token_obj.delete()
#             return Response({"status": True, "message": "Password reset successfully."}, status=status.HTTP_200_OK)
#         else:
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)