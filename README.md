# API Documentation

## Overview

This document provides an overview of the various API endpoints defined in your Django application. The API serves various functionalities related to salons, services, reviews, appointments, advertisements, and other auxiliary functions.

---

# Endpoints

## Routers

### Services
- **URL**: `/services/`
- **ViewSet**: `ServiceViewSet`
- **Methods**: GET, POST, PUT, PATCH, DELETE

### Reviews
- **URL**: `/reviews/`
- **ViewSet**: `ReviewViewSet`
- **Methods**: GET, POST, PUT, PATCH, DELETE

### Fixed Operating Hours
- **URL**: `/fixed-operating-hours/`
- **ViewSet**: `FixedOperatingHoursViewSet`
- **Methods**: GET, POST, PUT, PATCH, DELETE

### Unfixed Operating Hours
- **URL**: `/unfixed-operating-hours/`
- **ViewSet**: `UnFixedOperatingHoursViewSet`
- **Methods**: GET, POST, PUT, PATCH, DELETE

### Generated Time Slots
- **URL**: `/generatedtimeslots/`
- **ViewSet**: `GeneratedTimeSlotsViewSet`
- **Methods**: GET, POST, PUT, PATCH, DELETE

### Appointments
- **URL**: `/appointments/`
- **ViewSet**: `AppointmentViewSet`
- **Methods**: GET, POST, PUT, PATCH, DELETE

### Firebase Users
- **URL**: `/frb-users/`
- **ViewSet**: `FirebaseUsersViewSet`
- **Methods**: GET, POST, PUT, PATCH, DELETE

### Keywords
- **URL**: `/keywords/`
- **ViewSet**: `KeywordsCounterViewSet`
- **Methods**: GET, POST, PUT, PATCH, DELETE

---

## Path Endpoints

### Salon
- **URL**: `/salons/`
  - **Methods**: GET (list), POST (create)
  - **View**: `SalonViewSet`

- **URL**: `/salons/<int:pk>/`
  - **Methods**: GET (retrieve), PUT (update), PATCH (partial_update), DELETE (destroy)
  - **View**: `SalonViewSet`

- **URL**: `/get/salon/`
  - **Methods**: GET
  - **View**: `SalonGetView`

- **URL**: `/salon/<int:salon_id>/photos/<str:photo_type>/`
  - **Methods**: GET, POST, DELETE
  - **View**: `SalonImageViewFinal`

- **URL**: `/salon_image/delete/<int:pk>/`
  - **Methods**: DELETE
  - **View**: `DeleteSalonImageView`

- **URL**: `/salon/check/<int:salon_id>/`
  - **Methods**: GET
  - **View**: `check_salon`

- **URL**: `/salon/license/`
  - **Methods**: POST
  - **View**: `LicenseCreateView`

- **URL**: `/salon/license/<str:username>/`
  - **Methods**: GET
  - **View**: `LicenseDetailView`

- **URL**: `/salon/payment/`
  - **Methods**: POST
  - **View**: `AddPaymentView`

- **URL**: `/salon/license/status/<str:username>/`
  - **Methods**: GET
  - **View**: `LicenseStatusView`

### Services & Categories
- **URL**: `/salon/<int:salon_id>/services/`
  - **Methods**: GET
  - **View**: `SalonServiceListView`

- **URL**: `/categories/`
  - **Methods**: GET, POST, PUT, PATCH, DELETE
  - **View**: `CategoryViewSet`

- **URL**: `/categories_delete/<int:pk>/`
  - **Methods**: DELETE
  - **View**: `CategoryViewSet`

- **URL**: `/categories_update/<int:pk>/`
  - **Methods**: PUT, PATCH
  - **View**: `CategoryViewSet`

- **URL**: `/salons/<int:pk>/reviews/`
  - **Methods**: GET
  - **View**: `SalonReviews`

- **URL**: `/avatar-by-salon-name/<str:salon_avatar>/`
  - **Methods**: GET
  - **View**: `AvatarBySalonNameView`

### Search
- **URL**: `/search/`
  - **Methods**: GET
  - **View**: `SalonSearchAPIView`

- **URL**: `/search-keywords/`
  - **Methods**: GET
  - **View**: `SearchView`

### Appointments
- **URL**: `/salon/<int:salon_id>/appointments/`
  - **Methods**: GET
  - **View**: `AppointmentListView`

- **URL**: `/user-appointments/`
  - **Methods**: GET
  - **View**: `UserAppointmentsListView`

- **URL**: `/firebase-users/id/<str:firebase_uid>/`
  - **Methods**: GET
  - **View**: `FirebaseUserDetailView`

- **URL**: `/firebase-users/<int:pk>/`
  - **Methods**: GET
  - **View**: `FirebaseUserDetailView`

### Advertisements
- **URL**: `/advertisements-add/`
  - **Methods**: POST
  - **View**: `AdvertisementListCreateView`

- **URL**: `/all-advertisements/`
  - **Methods**: GET
  - **View**: `AdvertisementListView`

- **URL**: `/findovio-advertisements/`
  - **Methods**: POST
  - **View**: `FindovioAdvertisementListCreateView`

- **URL**: `/findovioadvertisements/<int:pk>/`
  - **Methods**: GET, PUT, PATCH, DELETE
  - **View**: `FindovioAdvertisementDetailView`

### Functions
- **URL**: `/get-cities/`
  - **Methods**: GET
  - **View**: `views.getTopCities`

- **URL**: `/check-name-exists/`
  - **Methods**: GET
  - **View**: `CheckNameExists`

---

## Media

### Static Files and Media

To serve static files and media:
- **MEDIA_URL**: URL to access media files
- **MEDIA_ROOT**: Root directory for media files

These configurations ensure that the media files uploaded via the API are accessible through the defined URLs.

---

## Conclusion

This document provides a comprehensive overview of the API endpoints, methods, and views available in your Django application. For detailed implementation, refer to the corresponding viewsets and views in your codebase.
