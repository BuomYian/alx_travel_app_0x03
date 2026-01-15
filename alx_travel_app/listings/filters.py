from django_filters import rest_framework as filters
from .models import Listing, Booking


class ListingFilter(filters.FilterSet):
    """
    FilterSet for Listing model with support for various search and filter options.
    """
    city = filters.CharFilter(field_name='city', lookup_expr='icontains')
    country = filters.CharFilter(field_name='country', lookup_expr='icontains')
    property_type = filters.CharFilter(
        field_name='property_type', lookup_expr='exact')
    min_price = filters.NumberFilter(
        field_name='price_per_night', lookup_expr='gte')
    max_price = filters.NumberFilter(
        field_name='price_per_night', lookup_expr='lte')
    min_bedrooms = filters.NumberFilter(
        field_name='bedrooms', lookup_expr='gte')
    max_guests = filters.NumberFilter(
        field_name='max_guests', lookup_expr='gte')
    is_active = filters.BooleanFilter(field_name='is_active')

    class Meta:
        model = Listing
        fields = ['city', 'country', 'property_type', 'min_price',
                  'max_price', 'min_bedrooms', 'max_guests', 'is_active']


class BookingFilter(filters.FilterSet):
    """
    FilterSet for Booking model with support for date range and status filtering.
    """
    status = filters.CharFilter(field_name='status', lookup_expr='exact')
    guest = filters.NumberFilter(field_name='guest', lookup_expr='exact')
    listing = filters.NumberFilter(field_name='listing', lookup_expr='exact')
    check_in_from = filters.DateFilter(
        field_name='check_in', lookup_expr='gte')
    check_in_to = filters.DateFilter(field_name='check_in', lookup_expr='lte')

    class Meta:
        model = Booking
        fields = ['status', 'guest', 'listing', 'check_in_from', 'check_in_to']
