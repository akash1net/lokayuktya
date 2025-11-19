from rest_framework import serializers
from .models import User, UserProfile
from django.contrib.auth.password_validation import validate_password
from djoser.conf import settings as djoser_settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

UserModel = get_user_model()

# Email Registration Serializer
class EmailRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, min_length=6)
    user_source = serializers.CharField(max_length=20)

    class Meta:
        model = UserModel
        fields = ['email', 'password', 'user_source']

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = UserModel.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user

# Phone Registration Serializer
class PhoneRegisterSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=15)
    email = serializers.CharField(max_length=100, required=False, allow_blank=True)
    full_name = serializers.CharField(max_length=100)
    father_name = serializers.CharField(max_length=100)
    date_of_birth = serializers.CharField(max_length=15)
    gender = serializers.CharField(max_length=50)
    user_source = serializers.CharField(max_length=50)

class ResendOtpSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=15)
    

# OTP Verification Serializer
class OTPVerifySerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=15)
    otp_code = serializers.CharField(max_length=6)

# Login Serializer
class LoginSerializer(serializers.Serializer):
    email = serializers.CharField()  # email or phone
    password = serializers.CharField(required=False)





class PasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(style={"input_type": "password"})

    def validate(self, attrs):
        user =  self.context['user'] # or self.context["request"].user
        # why assert? There are ValidationError / fail everywhere
        assert user is not None

        try:
            validate_password(attrs["new_password"], user)
        except ValidationError as e:
            raise serializers.ValidationError(
                {"new_password": list(e.messages)})
        return super().validate(attrs)


class PasswordRetypeSerializer(PasswordSerializer):
    confirm_password = serializers.CharField(style={"input_type": "password"})

    default_error_messages = {
        "password_mismatch":
            djoser_settings.CONSTANTS.messages.PASSWORD_MISMATCH_ERROR
    }

    def validate(self, attrs):
        attrs = super().validate(attrs)
        if attrs["new_password"] == attrs["confirm_password"]:
            return attrs
        else:
            self.fail("password_mismatch")