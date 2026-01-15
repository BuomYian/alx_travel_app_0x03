# Travel Booking Platform - Backend API

A Django-based REST API backend for a travel booking platform with support for property listings, booking reservations, and user reviews.

## Features

- **Property Listings Management**: Create, read, and manage travel property listings
- **Booking System**: Handle reservation requests with availability validation
- **Review System**: Allow guests to leave reviews and ratings for completed bookings
- **User Management**: Support for property owners and guest users
- **Database Seeding**: Populate database with sample data for testing

## Project Structure

```
listings/
├── models.py # Database models (Listing, Booking, Review)
├── serializers.py # DRF serializers for API responses
├── management/
│ ├── **init**.py
│ └── commands/
│ ├── **init**.py
│ └── seed.py # Management command to seed database
├── admin.py # Django admin configuration
├── apps.py # App configuration
├── tests.py # Unit tests
└── urls.py # API endpoints
```

## Models

### Listing

Represents a property available for booking.

**Fields:**

- `title`: Property name
- `description`: Detailed property description
- `property_type`: Type of accommodation (apartment, house, villa, etc.)
- `location`: Full address
- `city`, `country`: Location details
- `latitude`, `longitude`: Geographic coordinates
- `bedrooms`, `bathrooms`: Number of rooms
- `max_guests`: Maximum occupancy
- `price_per_night`: Nightly rate (Decimal)
- `availability_from`, `availability_to`: Booking window dates
- `amenities`: Comma-separated list of amenities
- `owner`: Foreign key to User (property owner)
- `image_url`: Optional URL to property image
- `rating`: Property rating (0.0-5.0)
- `is_active`: Listing visibility status
- `created_at`, `updated_at`: Timestamps

**Relationships:**

- One-to-Many with Booking
- One-to-Many with Review
- Many-to-One with User (owner)

### Booking

Represents a guest's reservation.

**Fields:**

- `listing`: Foreign key to Listing
- `guest`: Foreign key to User
- `check_in`, `check_out`: Reservation dates
- `number_of_guests`: Number of people
- `total_price`: Calculated booking cost
- `status`: Booking status (pending, confirmed, cancelled, completed)
- `special_requests`: Optional guest notes
- `created_at`, `updated_at`: Timestamps

**Relationships:**

- Many-to-One with Listing
- Many-to-One with User (guest)
- One-to-One with Review

**Constraints:**

- Unique constraint on (listing, check_in, check_out)
- Validation: check_out > check_in
- Validation: number_of_guests <= listing.max_guests

### Review

Represents a guest review for a completed booking.

**Fields:**

- `listing`: Foreign key to Listing
- `booking`: One-to-One relationship with Booking
- `guest`: Foreign key to User
- `title`: Review headline
- `comment`: Review text
- `rating`: Rating 1-5
- `is_verified_booking`: Indicates verified purchase
- `created_at`, `updated_at`: Timestamps

**Relationships:**

- Many-to-One with Listing
- One-to-One with Booking
- Many-to-One with User (guest)

## Serializers

### ListingSerializer

Serializes Listing model with related data.

**Additional Fields:**

- `amenities_list`: Amenities converted to list format
- `average_rating`: Calculated from related reviews
- `booking_count`: Count of confirmed bookings
- `reviews`: Nested ReviewSerializer

### BookingSerializer

Serializes Booking model with validation.

**Validation:**

- Check-out date must be after check-in date
- Number of guests cannot exceed listing max_guests

### ReviewSerializer

Serializes Review model with nested User data.

## Management Commands

### Seed Command

Populates database with sample travel data.

**Usage:**

```bash
python manage.py seed
```

**Created Data:**

- 5 sample property owners
- 10 sample guest users
- 8 property listings across different countries and property types
- 8 bookings with various statuses
- Multiple reviews for completed bookings

**Sample Data Includes:**

- Luxury beach villa in Maldives
- Cozy apartment in Paris
- Modern cabin in Swiss Alps
- Historic villa in Tuscany
- Beachfront resort in Bali
- Downtown hostel in Barcelona
- Luxury hotel suite in Tokyo
- Countryside house in New Zealand

## Setup Instructions

### 1. Install Dependencies

```bash
pip install django djangorestframework
```

### 2. Create Migrations

```bash
python manage.py makemigrations listings
```

### 3. Apply Migrations

```bash
python manage.py migrate
```

### 4. Seed Database

```bash
python manage.py seed
```

### 5. Create Superuser (Optional)

```bash
python manage.py createsuperuser
```

### 6. Run Development Server

```bash
python manage.py runserver
```

## API Endpoints

### Listings

- `GET /api/listings/` - List all listings
- `POST /api/listings/` - Create new listing
- `GET /api/listings/{id}/` - Retrieve listing details
- `PUT /api/listings/{id}/` - Update listing
- `DELETE /api/listings/{id}/` - Delete listing

### Bookings

- `GET /api/bookings/` - List all bookings
- `POST /api/bookings/` - Create new booking
- `GET /api/bookings/{id}/` - Retrieve booking details
- `PUT /api/bookings/{id}/` - Update booking
- `DELETE /api/bookings/{id}/` - Cancel booking

### Reviews

- `GET /api/reviews/` - List all reviews
- `POST /api/reviews/` - Create new review
- `GET /api/reviews/{id}/` - Retrieve review details
- `PUT /api/reviews/{id}/` - Update review

## Data Validation

- **Listing**: Non-negative room counts, positive price, valid dates
- **Booking**: Valid date range, guest count within limits, duplicate booking prevention
- **Review**: Rating 1-5, required title and comment

## Testing the Seeder

1. Clear existing data (optional):

   ```bash
   python manage.py flush
   ```

2. Run seeder:

   ```bash
   python manage.py seed
   ```

3. Verify data in Django admin:
   ```bash
   python manage.py runserver
   ```

# Visit http://localhost:8000/admin/

````

4. Check API responses:
   ```bash
   curl http://localhost:8000/api/listings/
````

## Best Practices

- Always validate booking dates and guest counts
- Use DRF serializers for input validation
- Implement pagination for list endpoints
- Add authentication for booking and review creation
- Use database indexes for frequently queried fields
- Implement soft deletes for sensitive data
- Add rate limiting for API endpoints
- Use caching for frequently accessed listings

## Performance Optimization

- Database indexes on frequently queried fields (city, status)
- Nested serializers with `read_only=True` for API responses
- Pagination support in list views
- Select_related/prefetch_related for related objects

## Future Enhancements

- Payment integration (Stripe, PayPal)
- Email notifications for bookings
- Advanced search and filtering
- Wishlist/favorites feature
- User profile management
- Rating calculation aggregation
- Booking confirmation workflow
- Review moderation system

## Chapa Payment Integration

This project includes a basic integration with the Chapa payment gateway. The implementation includes:

- A `Payment` model (in `listings/models.py`) that tracks transactions for a `Booking`.
- Endpoints on the `BookingViewSet` to initiate and verify payments:
   - `POST /api/bookings/{id}/initiate_payment/` — Calls Chapa to create a checkout session and returns a `checkout_url`.
   - `GET /api/bookings/{id}/verify_payment/` — Verifies the transaction with Chapa and updates payment/booking status.

Configuration (set in environment or `.env`):

- `CHAPA_SECRET_KEY` — Your Chapa secret API key.
- `CHAPA_BASE_URL` — Optional base URL for Chapa API (default `https://api.chapa.co/v1`).
- `SITE_URL` — Optional site base URL used to build return/verify links (default `http://localhost:8000`).

Quick start (sandbox testing):

1. Add the keys to your `.env`:

```bash
CHAPA_SECRET_KEY=your_chapa_secret_key_here
CHAPA_BASE_URL=https://api.chapa.co/v1
SITE_URL=http://localhost:8000
```

2. Run migrations and start the server:

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```

3. Create a booking via the API and then call `initiate_payment` for that booking. Use the returned `checkout_url` to complete a sandbox payment, then call `verify_payment` to update the status and trigger a confirmation email.

Notes:

- The project includes a Celery task skeleton at `listings/tasks.py` (`send_payment_confirmation_email`). To send emails in the background, configure and run a Celery worker.
- The code attempts to fall back to synchronous email sending if Celery is not configured.
## License

This project is part of ALX Software Engineering Program training.

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss proposed changes.
