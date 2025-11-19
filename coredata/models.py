from django.db import models
from django.utils import timezone
from ckeditor.fields import RichTextField

class Banner(models.Model):
    PLATFORM_CHOICES = [
        ('web', 'Web'),
        ('app', 'App'),
        ('both', 'Both'),
    ]

    title = models.CharField(max_length=255)
    image = models.FileField(upload_to="banners/", blank=True, null=True)
    link = models.URLField(blank=True, null=True)
    is_clickable = models.BooleanField(default=False)  # 👈 new field
    platform_type = models.CharField(
        max_length=10,
        choices=PLATFORM_CHOICES,
        default='both'  # 👈 default 'both' means common for app & web
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.platform_type})"


class FAQ(models.Model):
    question = models.CharField(max_length=500)
    answer = models.TextField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.question


class StaticPage(models.Model):
    PAGE_CHOICES = [
        ('about', 'About Us'),
        ('citizens', 'Citizens Charter'),
        ('genesis', 'Genesis'),
        ('organization', 'Organization Chart'),
        ('lokayukta', 'Lokayukta - Hope of the Common Man'),
        ('corruption', 'An Anti-Dote for Corruption in Public Life'),
        ('wakeupcall', 'Wake up Call by Lokayukta'),
        ('investigation', 'Investigation 1998'),
        ('conditions', 'Conditions of Service 1998'),
        ('privacy', 'Privacy Policy'),
        ('contact', 'Contact Us'),
        
    ]

    page_type = models.CharField(max_length=50, choices=PAGE_CHOICES, unique=True)
    title = models.CharField(max_length=255, blank=True, null=True)
    content = RichTextField(blank=True, null=True)
    image = models.FileField(upload_to='staticpage_files/', blank=True, null=True)

    def __str__(self):
        return dict(self.PAGE_CHOICES).get(self.page_type, self.page_type)
    


from django.db import models

class Gallery(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    image = models.FileField(upload_to="gallery/")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    


#Notification in Old  site on home page
class Highlights(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    image = models.FileField(upload_to="notification_highlights/")
    highlight_date = models.DateField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    



class Lokayukta(models.Model):
    USERS = [
        ('previous', 'Previous'),
        ('present', 'Present')
    ]

    USERS_POSITION = [
        ('present', 'Present'),
        ('first', 'First'),
        ('second', 'Second'),
        ('third', 'Third'),
        ('fourth', 'Fourth'),
        ('fifth', 'Fifth'),
        ('sixth', 'Sixth'),
        ('seventh', 'Seventh'),
        ('eighth', 'Eighth'),
        ('ninth', 'Ninth'),
        ('tenth', 'Tenth'),
    ]

    title = models.CharField(max_length=255)
    description = RichTextField(blank=True, null=True)
    image = models.FileField(upload_to="lokayukta_profiles_image/")
    lokayukta_status = models.CharField(max_length=50, choices=USERS, blank=True, null=True)
    user_position = models.CharField(max_length=50, choices=USERS_POSITION, unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    



class Country(models.Model):
    name = models.CharField(max_length=100, unique=True)  # Country name (e.g., India)
    iso_code = models.CharField(max_length=3, unique=True)  # ISO code (e.g., IND)
    phone_code = models.CharField(max_length=10, blank=True, null=True)  # e.g., +91
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "country_master"
        verbose_name = "Country"
        verbose_name_plural = "Countries"


class State(models.Model):
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name="states")
    name = models.CharField(max_length=100)  # State name (e.g., Maharashtra)
    code = models.CharField(max_length=10, blank=True, null=True)  # Optional (e.g., MH)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return f"{self.name}, {self.country.name}"

    class Meta:
        db_table = "state_master"
        verbose_name = "State"
        verbose_name_plural = "States"
        unique_together = ('country', 'name')  # Prevent duplicate state names in same country

