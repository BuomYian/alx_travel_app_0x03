from django.contrib import admin
from .models import Listing, Booking, Review


@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    """
    Admin interface for Listing model.
    """
    list_display = ['title', 'city', 'country', 'property_type',
                    'price_per_night', 'owner', 'is_active', 'created_at']
    list_filter = ['property_type', 'is_active',
                   'city', 'country', 'created_at']
    search_fields = ['title', 'description', 'city', 'country', 'location']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'property_type', 'owner')
        }),
        ('Location', {
            'fields': ('location', 'city', 'country', 'latitude', 'longitude')
        }),
        ('Property Details', {
            'fields': ('bedrooms', 'bathrooms', 'max_guests')
        }),
        ('Pricing & Availability', {
            'fields': ('price_per_night', 'available_from', 'available_to')
        }),
        ('Amenities & Media', {
            'fields': ('amenities', 'image_url')
        }),
        ('Metadata', {
            'fields': ('rating', 'is_active', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    """
    Admin interface for Booking model.
    """
    list_display = ['id', 'guest', 'listing', 'check_in',
                    'check_out', 'status', 'total_price', 'created_at']
    list_filter = ['status', 'created_at', 'check_in']
    search_fields = ['guest__username', 'listing__title', 'id']
    readonly_fields = ['created_at', 'updated_at', 'total_price']
    fieldsets = (
        ('Booking Information', {
            'fields': ('listing', 'guest', 'status')
        }),
        ('Dates', {
            'fields': ('check_in', 'check_out')
        }),
        ('Guest Details', {
            'fields': ('number_of_guests', 'special_requests')
        }),
        ('Pricing', {
            'fields': ('total_price',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """
    Admin interface for Review model.
    """
    list_display = ['id', 'listing', 'guest',
                    'rating', 'is_verified', 'created_at']
    list_filter = ['rating', 'is_verified', 'created_at']
    search_fields = ['guest__username', 'listing__title', 'title', 'comment']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Review Information', {
            'fields': ('listing', 'booking', 'guest', 'is_verified')
        }),
        ('Content', {
            'fields': ('title', 'comment', 'rating')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
