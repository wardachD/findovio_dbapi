from django.urls import path, include
from . import views 
from .views import SalonViewSet, FirebaseUsersViewSet, FirebaseUserDetailView, ServiceViewSet, GeneratedTimeSlotsViewSet, SalonSearchAPIView, ReviewViewSet, SalonReviews, FixedOperatingHoursViewSet, UnFixedOperatingHoursViewSet, GeneratedTimeSlotsViewSet, AppointmentViewSet, UserAppointmentsListView, KeywordsCounterViewSet, AvatarBySalonNameView, AdvertisementListCreateView, AdvertisementListView, FindovioAdvertisementListCreateView, FindovioAdvertisementDetailView, CheckNameExists, SalonGetView, CategoryViewSet, SalonServiceListView, SalonImageViewFinal, DeleteSalonImageView, check_salon, AppointmentListView, LicenseCreateView, LicenseDetailView, AddPaymentView, LicenseStatusView, SearchView
from rest_framework.routers import DefaultRouter
from django.conf import settings
from django.conf.urls.static import static

router = DefaultRouter()
router.register(r'services', ServiceViewSet, basename='service')
router.register(r'reviews', ReviewViewSet)
router.register(r'fixed-operating-hours', FixedOperatingHoursViewSet)
router.register(r'unfixed-operating-hours', UnFixedOperatingHoursViewSet)
router.register(r'generatedtimeslots', GeneratedTimeSlotsViewSet)
router.register(r'appointments', AppointmentViewSet)
router.register(r'frb-users', FirebaseUsersViewSet)
router.register(r'keywords', KeywordsCounterViewSet)

urlpatterns = [
    path('', include(router.urls)),

    # Salon
    path('salons/', SalonViewSet.as_view({'get': 'list', 'post': 'create'}), name='salons-list'),
    path('salons/<int:pk>/', SalonViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='salons-detail'),
    path('get/salon/', SalonGetView.as_view(), name='salon-by-email'),
    path('salon/<int:salon_id>/photos/<str:photo_type>/', SalonImageViewFinal.as_view()),
    path('salon_image/delete/<int:pk>/', DeleteSalonImageView.as_view({'delete': 'destroy'})),
    path('salon/check/<int:salon_id>/', check_salon, name='check_salon'),
    path('salon/license/', LicenseCreateView.as_view(), name='create_license'),
    path('salon/license/<str:username>/', LicenseDetailView.as_view(), name='license_detail'),
    path('salon/payment/', AddPaymentView.as_view(), name='add_payment'),
    path('salon/license/status/<str:username>/', LicenseStatusView.as_view(), name='license_status'),

    # Services & Categories
    path('salon/<int:salon_id>/services/', SalonServiceListView.as_view(), name='salon-services'),
    path('categories/', CategoryViewSet.as_view({'get': 'list', 'post': 'create', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='categories'),
    path('categories_delete/<int:pk>/', CategoryViewSet.as_view({'delete': 'destroy'}), name='categories_delete'),
    path('categories_update/<int:pk>/', CategoryViewSet.as_view({'put': 'update', 'patch': 'partial_update',}), name='categories_update'),
    path('salons/<int:pk>/reviews/', SalonReviews.as_view(), name='salon-reviews'),
    path('avatar-by-salon-name/<str:salon_avatar>', AvatarBySalonNameView.as_view(), name='avatar-by-salon-name'),


    # Search
    path('search/', SalonSearchAPIView.as_view(), name='salon-search'),
    path('search-keywords/', SearchView.as_view(), name='search-keywords'),


    # Appointments
    path('salon/<int:salon_id>/appointments/', AppointmentListView.as_view(), name='salon-appointments'),
    path('user-appointments/', UserAppointmentsListView.as_view(), name='user-appointments-list'),
    path('firebase-users/id/<str:firebase_uid>/', FirebaseUserDetailView.as_view()),
    path('firebase-users/<int:pk>/', FirebaseUserDetailView.as_view(), name='username'),


    # Advertisements
    path('advertisements-add/', AdvertisementListCreateView.as_view(), name='advertisement-list-create'),
    path('all-advertisements/', AdvertisementListView.as_view(), name='advertisement-list'),
    path('findovio-advertisements/', FindovioAdvertisementListCreateView.as_view(), name='advertisement-list'),
    path('findovioadvertisements/<int:pk>/', FindovioAdvertisementDetailView.as_view(), name='advertisement-detail'),

    
    # Functions
    path('get-cities/', views.getTopCities, name='getTopCities'),
    path('check-name-exists/', CheckNameExists.as_view(), name='check_name_exists'),
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)