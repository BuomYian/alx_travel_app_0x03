from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ListingViewSet, BookingViewSet, ReviewViewSet

# Create a router and register the viewsets
router = DefaultRouter()
router.register(r'listings', ListingViewSet, basename='listing')
router.register(r'bookings', BookingViewSet, basename='booking')
router.register(r'reviews', ReviewViewSet, basename='review')

# The API URLs are determined automatically by the router
urlpatterns = [
    path('', include(router.urls)),
]
