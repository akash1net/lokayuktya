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


urlpatterns = [
    path('', include(router.urls)),

]
