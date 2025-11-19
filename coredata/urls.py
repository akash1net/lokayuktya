from django.urls import path, include
from .views import *
from rest_framework.routers import SimpleRouter
from rest_framework.routers import DefaultRouter  

router = SimpleRouter()
router.register('banner', BannerViewSet, basename="Banner"),
router.register('faq', FAQViewSet, basename="FAQ"),
router.register('gallery', GalleryViewSet, basename="Gallery"),
router.register('notification-highlights', HighlightsViewSet, basename="Notification-Highlights"),
router.register('lokayukta-profile', LokayuktaViewSet, basename="Lokayukta-Profile"),
router.register('country', CountryViewSet, basename="country"),
router.register('state', StateViewSet, basename="state"),
router.register('static-pages', StaticPageViewSet, basename='staticpage'),



app_name = 'coredata'
urlpatterns = [
    path('', include(router.urls)),
]
