from django.db import models
from django.utils import timezone
from ckeditor.fields import RichTextField
from accounts.models import User, UserProfile
from coredata.models import Country
# from djoser.conf import settings as djoser_settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
import mimetypes
import uuid


class ComplaintCapacity(models.Model):
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Documents(models.Model):
    DOCUMENT_TYPES = (
        ('Affidavit', 'affidavit'),
        
    )
    document_type = models.CharField(
        max_length=50,
        choices=DOCUMENT_TYPES,
        null=True,
        blank=True
    )
    document_file = models.FileField(
        upload_to='complaint_affidavit/',
        null=True,
        blank=True
    )
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    

class Designation(models.Model):
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    

class PublicServient(models.Model):
    name = models.CharField(max_length=255)
    designation = models.ForeignKey(
        Designation,
        on_delete=models.SET_NULL,
        null=True,
        blank= True,
        related_name='designation'
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    

class Respondent(models.Model):
    """
    Person or official against whom the complaint is made.
    """
    name = models.CharField(max_length=255,blank=True, null=True)
    designation = models.CharField(max_length=255, blank=True, null=True)
    respondent_designation = models.ForeignKey(
        Designation,
        on_delete=models.SET_NULL,
        null=True,
        blank= True,
        related_name='respondent_designation_name'
    )
    public_servient_name = models.ForeignKey(
        PublicServient,
        on_delete=models.SET_NULL,
        null=True,
        blank= True,
        related_name='public_servient_name'
    )
    department = models.CharField(max_length=255, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        public_servient = self.public_servient_name.name if self.public_servient_name else "N/A"
        return f"{self.id}-{public_servient}"
    
class PublicFunctionary(models.Model):
    """
    Represents a public functionary (official) related to a complaint.
    Each has one file (like photo, ID, order copy, etc.)
    and can be linked to multiple complaints.
    """
    functionari_name = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Functionary #{self.functionari_name} - {self.id}"  
        

class Complaint(models.Model):
    complaint_no = models.CharField(
        max_length=30,
        unique=True,
        editable=False
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='user_complaint'
    )
    complaint_capacity = models.ForeignKey(
        ComplaintCapacity,
        on_delete=models.SET_NULL,
        null=True,
        blank= True,
        related_name='complaint_capacity_name'
    )
    nationality = models.ForeignKey(
        Country,
        on_delete=models.SET_NULL,
        null=True,
        blank= True,
        related_name='nationality'
    )
    is_public_functionaries = models.BooleanField(
        default=False,
        help_text="User Yes to  Public Functionaries"
    )
    post_name = models.CharField(max_length=250, blank=True, null=True)
    public_functionaries = models.ManyToManyField(
        PublicFunctionary,
        related_name='complaints_public_functionaries',
        blank=True
    )
    complaint_text = RichTextField()
    status = models.CharField(
        max_length=50,
        choices=[
            ('pending', 'Pending'),
            ('Review', 'Review'),
            ('in_progress', 'In Progress'),
            ('resolved', 'Resolved'),
            ('rejected', 'Rejected'),
        ],
        default='pending'
    )
    respondent = models.ForeignKey(
        Respondent,
        on_delete=models.SET_NULL,
        null=True,
        related_name='respondent_detail'
    )
    declaration_accepted = models.BooleanField(
        default=False,
        help_text="User agrees to the declaration statement."
    )
    signature = models.ImageField(
        upload_to='complaints/signatures/',
        blank=True, null=True,
        help_text="Digital signature or uploaded image of signature."
    )
    affidavit = models.FileField(
        upload_to='complaints/affidavit/',
        blank=True, null=True,
        help_text="Digital affidavit or uploaded image of Affidavit."
    )
    
    is_fee_verified = models.BooleanField(
        default=False,
        help_text="Verification checkbox (True/False)."
    )
    is_affidavit = models.BooleanField(
        default=False,
        help_text="User agrees to the verify Mobile."
    )
    confirm_accepted = models.BooleanField(
        default=False,
        help_text="User agrees to the confirm statement."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def save(self, *args, **kwargs):
        if not self.complaint_no:
            # Generate unique complaint number e.g. DLK-2025-022042323
            current_year = timezone.now().year
            random_part = uuid.uuid4().int % 10000000  # 8-digit random number
            self.complaint_no = f"DLK-{current_year}-{random_part:08d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Complaint #{self.id}-{self.complaint_no}-{self.user.phone}"


class ComplaintDocument(models.Model):
    complaint = models.ForeignKey(
        Complaint,
        on_delete=models.CASCADE,
        related_name='documents'
    )
    document_type = models.ForeignKey(
        Documents,
        on_delete=models.SET_NULL,
        null=True,
        related_name='complaint_documents'
    )
    document_number = models.CharField(max_length=100, blank=True, null=True)
    document_image = models.ImageField(upload_to='complaints/documents/', blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.complaint.complaint_no}-{self.document_type} ({self.document_number})"
    
  
class EvidenceDocument(models.Model):
    complaint = models.ForeignKey(
        Complaint,
        on_delete=models.SET_NULL,   # complaint bane pe attach karenge
        null=True,
        blank=True,
        related_name='evidences'
    )
    evidence_file = models.FileField(upload_to='complaints/evidences/')
    description = models.TextField(blank=True, null=True)
    file_type = models.CharField(max_length=50, blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.evidence_file:
            mime_type, _ = mimetypes.guess_type(self.evidence_file.name)
            if mime_type:
                if mime_type.startswith('image'):
                    self.file_type = 'image'
                elif mime_type.startswith('video'):
                    self.file_type = 'video'
                elif mime_type.startswith('audio'):
                    self.file_type = 'audio'
                elif mime_type == 'application/pdf':
                    self.file_type = 'pdf'
                else:
                    self.file_type = 'other'
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Evidence #{self.id} ({self.file_type})"
    

class FollowUpNote(models.Model):
    complaint = models.ForeignKey(
        Complaint,
        on_delete=models.SET_NULL,   # complaint bane pe attach karenge
        null=True,
        blank=True,
        related_name='followup_note'
    )
    description = models.TextField(blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)


class FollowUpDocument(models.Model):
    complaint = models.ForeignKey(
        Complaint,
        on_delete=models.SET_NULL,   # complaint bane pe attach karenge
        null=True,
        blank=True,
        related_name='followup_documents'
    )
    evidence_file = models.FileField(upload_to='complaints/followup/')
    file_type = models.CharField(max_length=50, blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    def save(self, *args, **kwargs):
        if self.evidence_file:
            mime_type, _ = mimetypes.guess_type(self.evidence_file.name)
            if mime_type:
                if mime_type.startswith('image'):
                    self.file_type = 'image'
                elif mime_type.startswith('video'):
                    self.file_type = 'video'
                elif mime_type.startswith('audio'):
                    self.file_type = 'audio'
                elif mime_type == 'application/pdf':
                    self.file_type = 'pdf'
                else:
                    self.file_type = 'other'
        super().save(*args, **kwargs)

    def __str__(self):
        return f"FollowUp #{self.id} ({self.file_type})"

    










