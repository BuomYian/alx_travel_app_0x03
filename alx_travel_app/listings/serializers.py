from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Listing, Booking, Review


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model."""
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = ['id']


class ReviewSerializer(serializers.ModelSerializer):
    """Serializer for Review model."""
    guest = UserSerializer(read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'listing', 'booking', 'guest', 'title',
                  'comment', 'rating', 'created_at', 'is_verified']
        read_only_fields = ['id', 'created_at', 'guest']


class ListingSerializer(serializers.ModelSerializer):
    """Serializer for Listing model."""
    owner = UserSerializer(read_only=True)
    reviews = ReviewSerializer(many=True, read_only=True)
    amenities_list = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()
    booking_count = serializers.SerializerMethodField()

    class Meta:
        model = Listing
        fields = [
            'id',
            'title',
            'description',
            'property_type',
            'location',
            'city',
            'country',
            'latitude',
            'longitude',
            'bedrooms',
            'bathrooms',
            'max_guests',
            'price_per_night',
            'available_from',
            'available_to',
            'amenities',
            'amenities_list',
            'owner',
            'image_url',
            'rating',
            'average_rating',
            'booking_count',
            'reviews',
            'created_at',
            'updated_at',
            'is_active',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'owner']

    def get_amenities_list(self, obj):
        """Convert comma-separated amenities string to list."""
        return [a.strip() for a in obj.amenities.split(',') if a.strip()]

    def get_average_rating(self, obj):
        """Calculate average rating from reviews."""
        reviews = obj.reviews.all()
        if reviews:
            return sum(r.rating for r in reviews) / len(reviews)
        return 0.0

    def get_booking_count(self, obj):
        """Return count of confirmed bookings."""
        return obj.bookings.filter(status='confirmed').count()


class BookingSerializer(serializers.ModelSerializer):
    """Serializer for Booking model."""
    listing = ListingSerializer(read_only=True)
    guest = UserSerializer(read_only=True)
    listing_id = serializers.PrimaryKeyRelatedField(
        queryset=Listing.objects.all(),
        source='listing',
        write_only=True
    )

    class Meta:
        model = Booking
        fields = [
            'id',
            'listing',
            'listing_id',
            'guest',
            'check_in',
            'check_out',
            'number_of_guests',
            'total_price',
            'status',
            'special_requests',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at',
                            'updated_at', 'guest', 'total_price']

    def validate(self, data):
        """Validate booking dates and guest count."""
        if data['check_in'] >= data['check_out']:
            raise serializers.ValidationError(
                "Check-out date must be after check-in date.")

        listing = data['listing']
        if data['number_of_guests'] > listing.max_guests:
            raise serializers.ValidationError(
                f"Number of guests cannot exceed {listing.max_guests}."
            )

        return data
