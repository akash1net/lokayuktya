from django.contrib import admin

# Register your models here.

from .models import *
admin.site.register(ComplaintCapacity)
admin.site.register(Documents)
admin.site.register(Respondent)
admin.site.register(PublicFunctionary)
admin.site.register(Complaint)
admin.site.register(ComplaintDocument)
admin.site.register(EvidenceDocument)
admin.site.register(Designation)
admin.site.register(PublicServient)
admin.site.register(FollowUpNote)
admin.site.register(FollowUpDocument)



