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

## Celery & Background Tasks Configuration

This project uses Celery with RabbitMQ for handling background tasks, specifically sending booking confirmation emails asynchronously.

### Quick Setup

#### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

#### 2. Install and Start RabbitMQ

**Using Docker (Recommended):**
```bash
docker run -d --name rabbitmq -p 5672:5672 -p 15672:15672 \
  -e RABBITMQ_DEFAULT_USER=guest \
  -e RABBITMQ_DEFAULT_PASS=guest \
  rabbitmq:3-management
```

**Using Package Manager (Linux):**
```bash
sudo apt-get install rabbitmq-server
sudo systemctl start rabbitmq-server
```

#### 3. Configure Email in .env

```env
# Celery Configuration
CELERY_BROKER_URL=amqp://guest:guest@localhost:5672//
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Email Configuration (example with Gmail)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=true
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@alxtravelapp.com

# Or use console backend for development
# EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

#### 4. Start Celery Worker

In a new terminal window:

```bash
celery -A alx_travel_app worker -l info
```

#### 5. Run Django Development Server

```bash
python manage.py runserver
```

### Available Background Tasks

#### send_booking_confirmation_email(booking_id)

Sends a confirmation email when a new booking is created.

- **Triggered by**: `BookingViewSet.perform_create()`
- **Parameters**: booking_id (int)
- **Retries**: Up to 3 times with 60-second intervals
- **Features**: 
  - HTML email template support with plain text fallback
  - Guest name personalization
  - Includes booking details (dates, price, listing info)

#### send_payment_confirmation_email(booking_id)

Sends a confirmation email when payment is successfully completed.

- **Triggered by**: `BookingViewSet.verify_payment()` (when payment succeeds)
- **Parameters**: booking_id (int)
- **Retries**: Up to 3 times with 60-second intervals
- **Features**:
  - Confirms successful payment
  - Includes payment amount
  - Guest name personalization

### Testing Tasks

#### Via Django Shell

```bash
python manage.py shell
```

```python
from listings.models import Booking
from listings.tasks import send_booking_confirmation_email

# Find a booking
booking = Booking.objects.first()

# Trigger the task asynchronously
result = send_booking_confirmation_email.delay(booking.id)

# Check task status
print(result.state)      # PENDING, STARTED, SUCCESS, FAILURE
print(result.result)     # True or False
```

#### Via API

Create a new booking:
```bash
curl -X POST http://localhost:8000/api/listings/bookings/ \
  -H "Authorization: Bearer <your-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "listing": 1,
    "check_in": "2024-02-01",
    "check_out": "2024-02-05",
    "number_of_guests": 2
  }'
```

Watch the Celery worker logs for task execution.

### File Changes

**New Files:**
- `alx_travel_app/celery.py` - Celery configuration

**Modified Files:**
- `requirements.txt` - Added celery and kombu
- `alx_travel_app/settings.py` - Added Celery, email, and result backend configurations
- `alx_travel_app/__init__.py` - Initialize Celery app
- `listings/tasks.py` - Enhanced with robust email tasks
- `listings/views.py` - Added email task triggers in BookingViewSet

### Troubleshooting

**Tasks not executing?**
1. Ensure Celery worker is running: `celery -A alx_travel_app worker -l info`
2. Verify RabbitMQ is running and accessible
3. Check .env configuration for CELERY_BROKER_URL

**Emails not being sent?**
1. Verify EMAIL_HOST and EMAIL_HOST_PASSWORD in .env
2. For Gmail, use an app-specific password (not regular password)
3. Test with console backend: `EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend`
4. Check Celery worker logs for exceptions

**RabbitMQ connection issues?**
1. Verify RabbitMQ is running: `docker ps` (if using Docker)
2. Test connection: `telnet localhost 5672`
3. Check RabbitMQ logs for errors

### Additional Monitoring

Check active Celery tasks:
```bash
celery -A alx_travel_app inspect active
```

Monitor with Celery Flower (web UI):
```bash
pip install flower
celery -A alx_travel_app flower
# Access at http://localhost:5555
```

For more detailed information, see the comprehensive [Celery Setup Guide](CELERY_SETUP.md).

Notes:

- The project now uses Celery with RabbitMQ message broker for asynchronous task execution
- Email tasks have retry logic and proper error handling
- Tasks are auto-discovered from the listings app
- For development, you can use the console email backend to see emails in the terminal

## License

This project is part of ALX Software Engineering Program training.

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss proposed changes.
