from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class Listing(models.Model):
    """Model for travel property listings.
    Represents a property available for booking on the travel 
    Platform.
    """
    PROPERTY_TYPES = [
        ('apartment', 'Apartment'),
        ('house', 'House'),
        ('villa', 'Villa'),
        ('cabin', 'Cabin'),
        ('resort', 'Resort'),
        ('hostel', 'Hostel'),
        ('hotel', 'Hotel'),
    ]

    # Basic Information
    title = models.CharField(max_length=255)
    description = models.TextField()
    property_type = models.CharField(
        max_length=50,
        choices=PROPERTY_TYPES,
        default='apartment'
    )

    # Location Information
    location = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    # Property Details
    bedrooms = models.IntegerField(validators=[MinValueValidator(0)])
    bathrooms = models.IntegerField(validators=[MinValueValidator(0)])
    max_guests = models.IntegerField(validators=[MinValueValidator(1)])

    # Pricing Information
    price_per_night = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    available_from = models.DateField()
    available_to = models.DateField()

    # Amenities
    amenities = models.TextField(
        help_text="Comma-separated list of amenities"
    )

    # Host Information
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='listings'
    )

    # Metadata
    image_url = models.URLField(blank=True, null=True)
    rating = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(5.0)]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['city', 'country']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"{self.title} in {self.city}"


class Booking(models.Model):
    """
    Model for bookings reservations.
    Tracks when guests book a listing and their reservation details.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('canceled', 'Canceled'),
        ('completed', 'Completed'),
    ]

    # Foreign Keys
    listing = models.ForeignKey(
        Listing,
        on_delete=models.CASCADE,
        related_name='bookings'
    )
    guest = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='bookings'
    )

    # Booking Details
    check_in = models.DateField()
    check_out = models.DateField()
    number_of_guests = models.IntegerField(validators=[MinValueValidator(1)])
    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )

    # Status and Information
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    special_requests = models.TextField(blank=True, null=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ('listing', 'check_in', 'check_out')
        indexes = [
            models.Index(fields=['guest', 'status']),
            models.Index(fields=['listing', 'check_in', 'check_out']),
        ]

    def __str__(self):
        return f"Booking by {self.guest.username} for {self.listing.title} from {self.check_in} to {self.check_out}"


class Review(models.Model):
    """
    Model for guest reviews and ratings.
    Allows guests to review listings and provide feedback.
    """
    RATING_CHOICES = [
        (1, '1 - Poor'),
        (2, '2 - Fair'),
        (3, '3 - Good'),
        (4, '4 - Very Good'),
        (5, '5 - Excellent'),
    ]

    # Foreign Keys
    listing = models.ForeignKey(
        Listing, on_delete=models.CASCADE, related_name='reviews')
    booking = models.ForeignKey(
        Booking, on_delete=models.CASCADE, related_name='reviews')
    guest = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='reviews')

    # Review Details
    title = models.CharField(max_length=255)
    comment = models.TextField()
    rating = models.IntegerField(choices=RATING_CHOICES)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_verified = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']
        unique_together = ('booking',)
        indexes = [
            models.Index(fields=['listing', 'rating']),
        ]

    def __str__(self):
        return f"Review by {self.guest.username} for {self.listing.title} - {self.rating} Stars"


class Payment(models.Model):
    """
    Model to track payment transactions via Chapa.
    Linked to a Booking. Stores amount, status, and external transaction id.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]

    booking = models.ForeignKey(
        Booking, on_delete=models.CASCADE, related_name='payments'
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default='USD')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    transaction_id = models.CharField(max_length=255, blank=True, null=True, unique=False)
    chapa_response = models.JSONField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Payment {self.id} for Booking {self.booking.id} - {self.status}"
