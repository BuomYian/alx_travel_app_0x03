from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from datetime import datetime, timedelta
from decimal import Decimal
from listings.models import Listing, Booking, Review
import random


class Command(BaseCommand):
    help = "Seed the database with sample travel listings, bookings, and reviews"

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting database seeding...'))

        # Create sample users (owners and guests)
        owners = self._create_users(count=5, prefix='owner')
        guests = self._create_users(count=10, prefix='guest')

        # Create sample listings
        listings = self._create_listings(owners)

        # Create sample bookings
        bookings = self._create_bookings(listings, guests)

        # Create sample reviews
        self._create_reviews(bookings, guests)

        self.stdout.write(
            self.style.SUCCESS(
                f'Database seeding completed successfully!\n'
                f'Created {len(owners)} owners, {len(guests)} guests, '
                f'{len(listings)} listings, {len(bookings)} bookings'
            )
        )

    def _create_users(self, count, prefix):
        """Create sample users."""
        users = []
        for i in range(count):
            username = f'{prefix}_{i+1}'
            email = f'{username}@example.com'

            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': email,
                    'first_name': f'{prefix.capitalize()}',
                    'last_name': f'User{i+1}',
                }
            )
            if created:
                self.stdout.write(f'Created user: {username}')
            users.append(user)

        return users

    def _create_listings(self, owners):
        """Create sample listings."""
        listings_data = [
            {
                'title': 'Luxury Beach Villa in Maldives',
                'description': 'Beautiful beachfront villa with private pool and stunning ocean views.',
                'property_type': 'villa',
                'location': 'South Male Atoll, Maldives',
                'city': 'Male',
                'country': 'Maldives',
                'bedrooms': 4,
                'bathrooms': 3,
                'max_guests': 10,
                'price_per_night': Decimal('500.00'),
                'amenities': 'Pool, WiFi, AC, TV, Kitchen, Beach Access, Private Chef',
                'image_url': 'https://images.unsplash.com/photo-1470114716159-e389f8712fda?w=400',
                'rating': 4.8,
            },
            {
                'title': 'Cozy Apartment in Paris',
                'description': 'Charming 2-bedroom apartment in the heart of Paris, near Eiffel Tower.',
                'property_type': 'apartment',
                'location': '7th Arrondissement, Paris',
                'city': 'Paris',
                'country': 'France',
                'bedrooms': 2,
                'bathrooms': 1,
                'max_guests': 4,
                'price_per_night': Decimal('150.00'),
                'amenities': 'WiFi, AC, TV, Kitchen, Balcony, Metro Access',
                'image_url': 'https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?w=400',
                'rating': 4.6,
            },
            {
                'title': 'Modern Cabin in Swiss Alps',
                'description': 'Contemporary cabin nestled in the Swiss Alps with mountain views.',
                'property_type': 'cabin',
                'location': 'Valais, Swiss Alps',
                'city': 'Zermatt',
                'country': 'Switzerland',
                'bedrooms': 3,
                'bathrooms': 2,
                'max_guests': 8,
                'price_per_night': Decimal('250.00'),
                'amenities': 'Fireplace, WiFi, Heating, Hot Tub, Mountain View, Sauna',
                'image_url': 'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=400',
                'rating': 4.9,
            },
            {
                'title': 'Historic Villa in Tuscany',
                'description': 'Restored Renaissance villa surrounded by vineyards and olive groves.',
                'property_type': 'villa',
                'location': 'Val d\'Orcia, Tuscany',
                'city': 'Siena',
                'country': 'Italy',
                'bedrooms': 6,
                'bathrooms': 4,
                'max_guests': 12,
                'price_per_night': Decimal('400.00'),
                'amenities': 'Pool, Wine Cellar, Tennis Court, WiFi, Kitchen, Garden',
                'image_url': 'https://images.unsplash.com/photo-1512207736139-7c2d7a03d5b0?w=400',
                'rating': 4.7,
            },
            {
                'title': 'Beachfront Resort in Bali',
                'description': 'All-inclusive beachfront resort with multiple pools and water sports.',
                'property_type': 'resort',
                'location': 'Seminyak Beach, Bali',
                'city': 'Bali',
                'country': 'Indonesia',
                'bedrooms': 8,
                'bathrooms': 5,
                'max_guests': 16,
                'price_per_night': Decimal('300.00'),
                'amenities': 'Multiple Pools, Beach Access, Restaurant, Spa, WiFi, Water Sports',
                'image_url': 'https://images.unsplash.com/photo-1473095169519-e21eeae34e6f?w=400',
                'rating': 4.5,
            },
            {
                'title': 'Downtown Hostel in Barcelona',
                'description': 'Budget-friendly hostel in the vibrant heart of Barcelona.',
                'property_type': 'hostel',
                'location': 'Gothic Quarter, Barcelona',
                'city': 'Barcelona',
                'country': 'Spain',
                'bedrooms': 5,
                'bathrooms': 3,
                'max_guests': 20,
                'price_per_night': Decimal('50.00'),
                'amenities': 'WiFi, Shared Kitchen, Common Area, Tours, Bar',
                'image_url': 'https://images.unsplash.com/photo-1552321554-5fefe8c9ef14?w=400',
                'rating': 4.2,
            },
            {
                'title': 'Luxury Hotel Suite in Tokyo',
                'description': 'Premium suite with city views in a 5-star hotel in Shibuya.',
                'property_type': 'hotel',
                'location': 'Shibuya, Tokyo',
                'city': 'Tokyo',
                'country': 'Japan',
                'bedrooms': 2,
                'bathrooms': 2,
                'max_guests': 4,
                'price_per_night': Decimal('350.00'),
                'amenities': 'Gym, Spa, Restaurant, Bar, Concierge, WiFi, City View',
                'image_url': 'https://images.unsplash.com/photo-1566073771259-6a8506099945?w=400',
                'rating': 4.8,
            },
            {
                'title': 'Countryside House in New Zealand',
                'description': 'Spacious house with stunning views of rolling hills and valleys.',
                'property_type': 'house',
                'location': 'Waikato Region, North Island',
                'city': 'Hamilton',
                'country': 'New Zealand',
                'bedrooms': 4,
                'bathrooms': 2,
                'max_guests': 8,
                'price_per_night': Decimal('200.00'),
                'amenities': 'Garden, WiFi, Kitchen, Fireplace, Parking, Hiking Access',
                'image_url': 'https://images.unsplash.com/photo-1570129477492-45201b8c7e89?w=400',
                'rating': 4.4,
            },
        ]

        listings = []
        for i, listing_data in enumerate(listings_data):
            available_from = datetime.now().date()
            available_to = available_from + timedelta(days=365)

            listing, created = Listing.objects.get_or_create(
                title=listing_data['title'],
                defaults={
                    **listing_data,
                    'owner': owners[i % len(owners)],
                    'available_from': available_from,
                    'available_to': available_to,
                }
            )
            if created:
                self.stdout.write(f'Created listing: {listing.title}')
            listings.append(listing)

        return listings

    def _create_bookings(self, listings, guests):
        """Create sample bookings."""
        bookings = []
        booking_data = [
            {'listing': 0, 'check_in': 30, 'check_out': 35,
                'guests': 4, 'status': 'confirmed'},
            {'listing': 0, 'check_in': 50, 'check_out': 55,
                'guests': 6, 'status': 'completed'},
            {'listing': 1, 'check_in': 15, 'check_out': 20,
                'guests': 2, 'status': 'confirmed'},
            {'listing': 2, 'check_in': 10, 'check_out': 15,
                'guests': 4, 'status': 'confirmed'},
            {'listing': 3, 'check_in': 45, 'check_out': 52,
                'guests': 8, 'status': 'completed'},
            {'listing': 4, 'check_in': 20, 'check_out': 25,
                'guests': 10, 'status': 'confirmed'},
            {'listing': 5, 'check_in': 5, 'check_out': 8,
                'guests': 3, 'status': 'confirmed'},
            {'listing': 6, 'check_in': 60, 'check_out': 63,
                'guests': 2, 'status': 'completed'},
        ]

        for data in booking_data:
            listing = listings[data['listing']]
            guest = random.choice(guests)
            check_in = datetime.now().date() + timedelta(days=data['check_in'])
            check_out = datetime.now().date() + \
                timedelta(days=data['check_out'])
            num_guests = data['guests']
            num_nights = (check_out - check_in).days
            total_price = listing.price_per_night * num_nights

            booking, created = Booking.objects.get_or_create(
                listing=listing,
                check_in=check_in,
                check_out=check_out,
                defaults={
                    'guest': guest,
                    'number_of_guests': num_guests,
                    'total_price': total_price,
                    'status': data['status'],
                    'special_requests': random.choice([
                        'Early check-in preferred',
                        'Late checkout if possible',
                        'Quiet room',
                        '',
                    ]),
                }
            )
            if created:
                self.stdout.write(
                    f'Created booking: {guest.username} for {listing.title} '
                    f'({check_in} to {check_out})'
                )
            bookings.append(booking)

        return bookings

    def _create_reviews(self, bookings, guests):
        """Create sample reviews for completed bookings."""
        reviews_created = 0
        completed_bookings = [b for b in bookings if b.status == 'completed']

        for booking in completed_bookings:
            # Skip if a review for this booking already exists
            if booking.reviews.exists():
                continue

            review_texts = [
                {
                    'title': 'Amazing experience!',
                    'comment': 'The property exceeded all expectations. Beautiful location, great amenities, and fantastic hospitality. Highly recommended!',
                    'rating': 5,
                },
                {
                    'title': 'Great stay',
                    'comment': 'Very comfortable accommodations with excellent service. Everything was clean and well-maintained. Would definitely stay again.',
                    'rating': 4,
                },
                {
                    'title': 'Perfect vacation spot',
                    'comment': 'Could not ask for a better place to spend our holidays. The views were breathtaking and the owner was very helpful.',
                    'rating': 5,
                },
                {
                    'title': 'Good value for money',
                    'comment': 'Decent place with good facilities. The location is convenient for exploring the area. Minor issues but overall a good stay.',
                    'rating': 4,
                },
            ]

            review_data = random.choice(review_texts)
            review = Review.objects.create(
                listing=booking.listing,
                booking=booking,
                guest=booking.guest,
                title=review_data['title'],
                comment=review_data['comment'],
                rating=review_data['rating'],
                is_verified=True,
            )
            reviews_created += 1
            self.stdout.write(f'Created review: {review.title}')

        self.stdout.write(
            self.style.SUCCESS(f'Created {reviews_created} reviews')
        )
