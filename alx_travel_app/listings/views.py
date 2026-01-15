from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Q, Avg
from datetime import datetime
import time
import requests
from django.conf import settings

from .models import Listing, Booking, Review
from .serializers import ListingSerializer, BookingSerializer, ReviewSerializer, UserSerializer
from .permissions import IsOwnerOrReadOnly, IsGuestOrReadOnly, IsReviewOwner
from .models import Payment
from .filters import ListingFilter, BookingFilter


class StandardResultsSetPagination(PageNumberPagination):
    """
    Standard pagination for API responses.
    """
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class ListingViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Listing model.
    Provides list, create, retrieve, update, and delete operations.
    """
    queryset = Listing.objects.all()
    serializer_class = ListingSerializer
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ListingFilter
    search_fields = ['title', 'description', 'city', 'country', 'location']
    ordering_fields = ['price_per_night', 'created_at', 'rating']
    ordering = ['-created_at']

    def perform_create(self, serializer):
        """
        Set the current user as the owner when creating a new listing.
        """
        serializer.save(owner=self.request.user)

    def get_queryset(self):
        """
        Filter listings based on query parameters.
        Supports filtering by availability dates.
        """
        queryset = super().get_queryset()

        # Filter by availability dates if provided
        check_in = self.request.query_params.get('check_in')
        check_out = self.request.query_params.get('check_out')

        if check_in and check_out:
            try:
                check_in_date = datetime.strptime(check_in, '%Y-%m-%d').date()
                check_out_date = datetime.strptime(
                    check_out, '%Y-%m-%d').date()

                queryset = queryset.filter(
                    Q(availability_from__lte=check_in_date) &
                    Q(availability_to__gte=check_out_date) &
                    Q(is_active=True)
                )
            except ValueError:
                pass

        return queryset

    @action(detail=False, methods=['get'])
    def available(self, request):
        """
        Get available listings for specific dates.
        Query params: check_in (YYYY-MM-DD), check_out (YYYY-MM-DD)
        """
        check_in = request.query_params.get('check_in')
        check_out = request.query_params.get('check_out')

        if not check_in or not check_out:
            return Response(
                {'error': 'check_in and check_out parameters are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            check_in_date = datetime.strptime(check_in, '%Y-%m-%d').date()
            check_out_date = datetime.strptime(check_out, '%Y-%m-%d').date()

            if check_in_date >= check_out_date:
                return Response(
                    {'error': 'check_out date must be after check_in date'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Get listings that are available and have no conflicting bookings
            available_listings = Listing.objects.filter(
                availability_from__lte=check_in_date,
                availability_to__gte=check_out_date,
                is_active=True
            ).exclude(
                bookings__status__in=['pending', 'confirmed'],
                bookings__check_in__lt=check_out_date,
                bookings__check_out__gt=check_in_date
            ).distinct()

            page = self.paginate_queryset(available_listings)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            serializer = self.get_serializer(available_listings, many=True)
            return Response(serializer.data)

        except ValueError:
            return Response(
                {'error': 'Invalid date format. Use YYYY-MM-DD'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['get'])
    def reviews(self, request, pk=None):
        """
        Get all reviews for a specific listing.
        """
        listing = self.get_object()
        reviews = listing.reviews.all()
        page = self.paginate_queryset(reviews)

        if page is not None:
            serializer = ReviewSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def my_listings(self, request):
        """
        Get listings owned by the current user.
        Requires authentication.
        """
        if not request.user.is_authenticated:
            return Response(
                {'error': 'Authentication required'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        queryset = Listing.objects.filter(owner=request.user)
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class BookingViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Booking model.
    Provides list, create, retrieve, update, and delete operations.
    """
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated, IsGuestOrReadOnly]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = BookingFilter
    ordering_fields = ['created_at', 'check_in', 'check_out']
    ordering = ['-created_at']

    def perform_create(self, serializer):
        """
        Set the current user as the guest when creating a new booking.
        Calculate total price based on number of nights and price per night.
        Trigger booking confirmation email task.
        """
        listing = serializer.validated_data['listing']
        check_in = serializer.validated_data['check_in']
        check_out = serializer.validated_data['check_out']

        # Calculate total price
        number_of_nights = (check_out - check_in).days
        total_price = float(listing.price_per_night) * number_of_nights

        booking = serializer.save(
            guest=self.request.user, total_price=total_price)

        # Trigger email notification task asynchronously
        try:
            from .tasks import send_booking_confirmation_email
            send_booking_confirmation_email.delay(booking.id)
        except Exception as e:
            # Log the error but don't fail the request if email task fails
            print(f"Failed to trigger booking confirmation email: {str(e)}")

    @action(detail=True, methods=['post'])
    def initiate_payment(self, request, pk=None):
        """
        Initiate a payment for this booking via Chapa.
        Returns a checkout URL to redirect the user to.
        """
        booking = self.get_object()

        # Only the guest who made the booking can initiate payment
        if booking.guest != request.user:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

        # Create a Payment record
        payment = Payment.objects.create(
            booking=booking,
            amount=booking.total_price,
            currency='USD',
            status='pending'
        )

        # Build return/verify URL
        verify_url = request.build_absolute_uri(
            f"/api/listings/bookings/{booking.id}/verify_payment/")

        # Prepare payload for Chapa
        tx_ref = f"booking_{booking.id}_{int(time.time())}"
        payload = {
            'amount': str(float(booking.total_price)),
            'currency': payment.currency,
            'email': booking.guest.email or '',
            'first_name': booking.guest.first_name or '',
            'last_name': booking.guest.last_name or '',
            'tx_ref': tx_ref,
            'callback_url': verify_url,
            'return_url': verify_url,
        }

        headers = {
            'Authorization': f'Bearer {settings.CHAPA_SECRET_KEY}',
            'Content-Type': 'application/json'
        }

        try:
            init_url = f"{settings.CHAPA_BASE_URL}/transaction/initialize"
            resp = requests.post(init_url, json=payload,
                                 headers=headers, timeout=10)
            data = resp.json()
        except Exception as e:
            payment.status = 'failed'
            payment.chapa_response = {'error': str(e)}
            payment.save()
            return Response({'error': 'Failed to contact payment gateway'}, status=status.HTTP_502_BAD_GATEWAY)

        # Save response and transaction identifier
        payment.chapa_response = data
        # Try to extract transaction id / reference
        tx_id = None
        checkout_url = None
        if isinstance(data, dict):
            d = data.get('data') or {}
            tx_id = d.get('id') or d.get(
                'reference') or d.get('tx_ref') or tx_ref
            checkout_url = d.get('checkout_url') or d.get(
                'link') or d.get('checkoutUrl')

        payment.transaction_id = tx_id
        payment.save()

        if checkout_url:
            return Response({'checkout_url': checkout_url, 'payment_id': payment.id})

        return Response({'error': 'Could not initiate payment', 'response': data}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def verify_payment(self, request, pk=None):
        """
        Verify payment status with Chapa for this booking.
        Updates the Payment and Booking status accordingly.
        """
        booking = self.get_object()

        # Find the most recent payment for this booking
        payment = booking.payments.order_by('-created_at').first()
        if not payment:
            return Response({'error': 'No payment found for this booking'}, status=status.HTTP_404_NOT_FOUND)

        # Determine transaction id to verify
        tx = payment.transaction_id or request.query_params.get(
            'transaction_id')
        if not tx:
            return Response({'error': 'No transaction id available to verify'}, status=status.HTTP_400_BAD_REQUEST)

        headers = {'Authorization': f'Bearer {settings.CHAPA_SECRET_KEY}'}
        try:
            verify_url = f"{settings.CHAPA_BASE_URL}/transaction/verify/{tx}"
            resp = requests.get(verify_url, headers=headers, timeout=10)
            data = resp.json()
        except Exception as e:
            return Response({'error': 'Verification request failed', 'details': str(e)}, status=status.HTTP_502_BAD_GATEWAY)

        # Update payment record
        payment.chapa_response = data
        # Determine status from response
        status_str = 'failed'
        if isinstance(data, dict):
            # Many gateways put status in data.status or top-level status
            d = data.get('data') or {}
            gateway_status = d.get('status') or data.get(
                'status') or d.get('transaction_status')
            if gateway_status and str(gateway_status).lower() in ['success', 'completed', 'paid']:
                status_str = 'completed'
            else:
                status_str = 'failed'

        payment.status = status_str
        payment.save()

        # If completed, mark booking confirmed and send confirmation email
        if payment.status == 'completed':
            booking.status = 'confirmed'
            booking.save()
            try:
                # Import task lazily to avoid hard dependency if Celery not configured
                from .tasks import send_payment_confirmation_email
                send_payment_confirmation_email.delay(booking.id)
            except Exception:
                # If Celery is not available, try synchronous send
                try:
                    from django.core.mail import send_mail
                    send_mail(
                        'Booking confirmed',
                        f'Your booking {booking.id} is confirmed. Payment successful.',
                        None,
                        [booking.guest.email],
                        fail_silently=True,
                    )
                except Exception:
                    pass

        return Response({'payment_status': payment.status, 'response': data})

    def get_queryset(self):
        """
        Filter bookings based on user role.
        Owners can see bookings for their listings.
        Guests can see their own bookings.
        """
        user = self.request.user
        if user.is_authenticated:
            # Show own bookings and bookings for owned listings
            return Booking.objects.filter(
                Q(guest=user) | Q(listing__owner=user)
            )
        return Booking.objects.none()

    @action(detail=False, methods=['get'])
    def my_bookings(self, request):
        """
        Get bookings made by the current user.
        Requires authentication.
        """
        if not request.user.is_authenticated:
            return Response(
                {'error': 'Authentication required'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        queryset = Booking.objects.filter(guest=request.user)
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def property_bookings(self, request):
        """
        Get bookings for listings owned by the current user.
        Requires authentication.
        """
        if not request.user.is_authenticated:
            return Response(
                {'error': 'Authentication required'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        queryset = Booking.objects.filter(listing__owner=request.user)
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        """
        Confirm a pending booking (owner only).
        """
        booking = self.get_object()

        if booking.listing.owner != request.user:
            return Response(
                {'error': 'Only the property owner can confirm bookings'},
                status=status.HTTP_403_FORBIDDEN
            )

        if booking.status != 'pending':
            return Response(
                {'error': 'Only pending bookings can be confirmed'},
                status=status.HTTP_400_BAD_REQUEST
            )

        booking.status = 'confirmed'
        booking.save()
        serializer = self.get_serializer(booking)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """
        Cancel a booking (guest or owner).
        """
        booking = self.get_object()

        # Check permissions
        if booking.guest != request.user and booking.listing.owner != request.user:
            return Response(
                {'error': 'You do not have permission to cancel this booking'},
                status=status.HTTP_403_FORBIDDEN
            )

        if booking.status == 'completed':
            return Response(
                {'error': 'Cannot cancel a completed booking'},
                status=status.HTTP_400_BAD_REQUEST
            )

        booking.status = 'cancelled'
        booking.save()
        serializer = self.get_serializer(booking)
        return Response(serializer.data)


class ReviewViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Review model.
    Provides list, create, retrieve, update, and delete operations.
    """
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsReviewOwner]
    pagination_class = StandardResultsSetPagination
    ordering_fields = ['created_at', 'rating']
    ordering = ['-created_at']

    def perform_create(self, serializer):
        """
        Set the current user as the guest when creating a new review.
        """
        serializer.save(guest=self.request.user)

    def get_queryset(self):
        """
        Filter reviews based on query parameters.
        """
        queryset = super().get_queryset()

        # Filter by listing if provided
        listing_id = self.request.query_params.get('listing_id')
        if listing_id:
            queryset = queryset.filter(listing_id=listing_id)

        # Filter by booking if provided
        booking_id = self.request.query_params.get('booking_id')
        if booking_id:
            queryset = queryset.filter(booking_id=booking_id)

        return queryset

    @action(detail=False, methods=['get'])
    def my_reviews(self, request):
        """
        Get reviews written by the current user.
        Requires authentication.
        """
        if not request.user.is_authenticated:
            return Response(
                {'error': 'Authentication required'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        queryset = Review.objects.filter(guest=request.user)
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
