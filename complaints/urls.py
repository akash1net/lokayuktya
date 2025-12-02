from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register('public-functionaries', PublicFunctionaryViewSet, basename='public-functionary')
router.register('complaint-capacities', ComplaintCapacityViewSet, basename='complaint-capacity')
router.register('documents', DocumentsViewSet, basename='document')
router.register('complaint-register', ComplaintViewSet, basename='complaint-register')
router.register('designation', DesignationViewSet, basename='designations')
router.register('public-servient', PublicServientViewSet, basename='public-servients')
router.register('evidence', EvidenceViewSet, basename='evidence')
router.register('follow-up', FollowUpDocumentViewSet, basename='follow-up')
router.register('follow-link', ComplaintFollowUpViewSet, basename='follow-link')
router.register('complaint-tracking', ComplaintTrackingView, basename='complaint-tracking')






urlpatterns = [
    path('', include(router.urls)),

]
