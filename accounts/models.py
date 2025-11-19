import uuid
from datetime import timedelta
from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.contrib.auth.base_user import BaseUserManager

# ------------------------------------------------------
# User Manager
# ------------------------------------------------------
class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, phone=None, email=None, password=None, **extra_fields):
        """
        Create and save a User with the given phone/email and password.
        Either phone or email must be provided.
        """
        if not phone and not email:
            raise ValueError("The user must have either a phone or an email.")

        if email:
            email = self.normalize_email(email)
            extra_fields['email'] = email

        user = self.model(phone=phone, **extra_fields)

        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()

        user.save(using=self._db)
        return user

    def create_user(self, phone=None, email=None, password=None, **extra_fields):
        """Create a regular user."""
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        extra_fields.setdefault("is_active", True)
        return self._create_user(phone=phone, email=email, password=password, **extra_fields)

    def create_superuser(self, phone=None, email=None, password=None, **extra_fields):
        """Create a superuser (admin)."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if not password:
            raise ValueError("Superusers must have a password.")
        if not email:
            raise ValueError("Superusers must have an email address.")

        return self._create_user(phone=phone, email=email, password=password, **extra_fields)

# ------------------------------------------------------
# Abstract User
# ------------------------------------------------------
class AbstractPhoneUser(AbstractUser):
    username = None  # remove username field completely
    email = models.EmailField("Email Address", unique=False, null=True, blank=True)

    objects = UserManager()

    USERNAME_FIELD = "phone"   # login with phone
    REQUIRED_FIELDS = []       # email optional even for superuser

    groups = models.ManyToManyField(
        Group,
        related_name="custom_user_set",
        blank=True,
        help_text="The groups this user belongs to.",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name="custom_user_permissions_set",
        blank=True,
        help_text="Specific permissions for this user.",
    )

    def __str__(self):
        return self.email or str(self.id)


# ------------------------------------------------------
# User Model
# ------------------------------------------------------
class User(AbstractPhoneUser):
    phone = models.CharField("Phone", max_length=15, unique=True, null=True, blank=True)
    profile_pic = models.FileField("Profile Pic", upload_to="profile_photo", null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    user_roll = models.ForeignKey(
        "UserRoll", related_name="user_roll",
        on_delete=models.SET_NULL, null=True, blank=True
    )
    position = models.CharField("Position", max_length=100, null=True, blank=True)
    language = models.CharField("Language", max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        return str(self.phone or self.email or self.id)

# ------------------------------------------------------
# UserProfile Model
# ------------------------------------------------------
class UserProfile(models.Model):
    GENDER_CHOICES = (
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    )

    USER_SOURCE_CHOICES = (
        ('android', 'Android'),
        ('ios', 'iOS'),
        ('web', 'Web'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    full_name = models.CharField("First Name", max_length=150, null=True, blank=True)
    father_name = models.CharField("Father name", max_length=150, null=True, blank=True)
    last_name = models.CharField("Last Name", max_length=150, null=True, blank=True)
    date_of_birth = models.DateField("Date of Birth", null=True, blank=True)
    age = models.PositiveIntegerField(null=True, blank=True)
    gender = models.CharField("Gender", max_length=10, choices=GENDER_CHOICES, null=True, blank=True)
    user_source = models.CharField("User Source", max_length=20, choices=USER_SOURCE_CHOICES, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"

    def __str__(self):
        return f"{self.full_name or ''}".strip() or str(self.user)

# ------------------------------------------------------
# Authentication Backend
# ------------------------------------------------------
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model

UserModel = get_user_model()

class EmailOrPhoneBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        if not username:
            return None

        user = UserModel.objects.filter(Q(email__iexact=username) | Q(phone=username)).first()
        if not user:
            return None

        if password and user.check_password(password):
            return user

        # For OTP login, actual OTP verification must happen in view
        if not password:
            return user  # safe only if OTP verified in view

        return None

# ------------------------------------------------------
# User Roll and Permissions
# ------------------------------------------------------
class UserRoll(models.Model):
    CODE_PREFIX = "RL"
    name = models.CharField("Name", max_length=200)
    permission = models.ManyToManyField(
        "UserPermission",
        verbose_name="Permission",
        related_name="userroll_permission",
        blank=True,
        through="UserRolePermission"
    )
    can_edit = models.BooleanField(default=True, blank=True)

    def __str__(self):
        return str(self.name)

class UserPermission(models.Model):
    CODE_PREFIX = "PM"
    permission_name = models.CharField(max_length=100, null=True, blank=True)
    permission_code = models.CharField(max_length=100, null=True, blank=True)
    permission_status = models.BooleanField(verbose_name="Permission Status", default=True, null=True)

    def __str__(self):
        return self.permission_name

class UserRolePermission(models.Model):
    PERMISSION_LEVEL_CHOICES = (
        ('read', 'Read'),
        ('write', 'Write'),
        ('no_access', 'No Access'),
        ('only_me', 'Only Me'),
    )
    CODE_PREFIX = "PM"
    user_roll = models.ForeignKey("UserRoll", related_name="role_permissions", on_delete=models.SET_NULL, null=True, blank=True)
    user_permission = models.ForeignKey("UserPermission", related_name="role_permissions", on_delete=models.CASCADE, blank=True, null=True)
    permission_level = models.CharField(max_length=20, choices=PERMISSION_LEVEL_CHOICES, default='write')

    def __str__(self):
        return f"{self.user_roll} → {self.user_permission} ({self.permission_level})"

# ------------------------------------------------------
# OTP Model
# ------------------------------------------------------
class OTP(models.Model):
    OTP_TYPE_CHOICES = (
        ('email', 'Email'),
        ('phone', 'Phone'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="otps", blank=True, null=True )
    phone = models.CharField(max_length=20, null=False, blank=False)
    otp_code = models.CharField("OTP Code", max_length=6)
    otp_type = models.CharField("OTP Type", max_length=10, choices=OTP_TYPE_CHOICES)
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    class Meta:
        verbose_name = "OTP"
        verbose_name_plural = "OTPs"

    def __str__(self):
        return f"{self.user} - {self.otp_code} ({self.otp_type})"

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(minutes=5)
        super().save(*args, **kwargs)

    def is_expired(self):
        return timezone.now() > self.expires_at
