from django.contrib import admin

# Register your models here.
from .models import *
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserProfile, OTP

# Custom User admin
@admin.register(User)
class CustomUserAdmin(BaseUserAdmin):
    model = User
    list_display = ('id', 'email', 'phone', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active')
    ordering = ('email',)
    search_fields = ('email', 'phone')

    fieldsets = (
        (None, {'fields': ('email', 'phone', 'password')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'phone', 'password1', 'password2', 'is_staff', 'is_active')}
        ),
    )

# Optional: UserProfile admin
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('id','user_source','full_name', 'last_name', 'date_of_birth', 'age')
    search_fields = ('full_name', 'last_name')
    ordering = ('last_name',)
    



@admin.register(OTP)
class OTPAdmin(admin.ModelAdmin):
    list_display = ('id','user','phone','otp_code','is_used','created_at')
    ordering = ('-created_at',)

admin.site.register(UserPermission)
admin.site.register(UserRolePermission)








