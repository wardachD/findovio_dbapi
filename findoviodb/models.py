from django.utils import timezone
from datetime import datetime, timedelta
from django.contrib.gis.db import models
from django.contrib.gis.geos import Point
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable, GeocoderServiceError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.postgres.fields import ArrayField

class Salon(models.Model):
    FLUTTER_CATEGORY_CHOICES = (
        ('Fryzjer', 'Hairdresser'),
        ('Paznokcie', 'Nails'),
        ('Masaż', 'Massage'),
        ('Barber', 'Barber'),
        ('Makijaż', 'Makeup'),
        ('Pielęgnacja dłoni', 'Pedicure'),
        ('Pielęgnacja stóp', 'Manicure')
    )
    FLUTTER_GENDER_CHOICES = (
        ('man', 'man'),
        ('woman', 'woman'),
        ('both', 'both')
    )
    SALON_PROPERTIES = [
        (0, 'Nowy'),
        (1, 'Numer zweryfikowany'),
        (2, 'Salon zweryfikowany'),
        (3, 'Język angielski'),
        (4, 'Polecany'),
        (5, 'Ma galerię'),
        (6, 'Opcja dojazdu'),
        (7, 'Dla dzieci'),
    ]
    

    name = models.CharField(max_length=100)
    address_city = models.CharField(max_length=100)
    address_postal_code = models.CharField(max_length=20)
    address_street = models.CharField(max_length=100)
    address_number = models.CharField(max_length=10)
    location = models.PointField(default=Point(0, 0), srid=4326)
    about = models.TextField(max_length=200)
    avatar = models.URLField(max_length=120, null=True, blank=True, default='')
    gallery = ArrayField(models.URLField(max_length=200), default=list, blank=True)
    phone_number = models.CharField(max_length=20, default='')
    distance_from_query = models.FloatField(null=True, blank=True, default=1.0)
    error_code = models.PositiveSmallIntegerField(default=1, blank=True)
    flutter_category = models.CharField(max_length=30, choices=FLUTTER_CATEGORY_CHOICES, default='hairdresser')
    flutter_gender_type = models.CharField(max_length=8, choices=FLUTTER_GENDER_CHOICES, default='both')
    codes = ArrayField(models.PositiveSmallIntegerField(choices=SALON_PROPERTIES), default=list, blank=True)
    email = models.EmailField(max_length=60, null=True, blank=True, default='')
    
    def update_average_rating(self):
        reviews = self.reviews.all()
        if reviews.exists():
            average_rating = reviews.aggregate(Avg('rating'))['rating__avg']
            self.review = round(average_rating, 1)
        else:
            self.review = 0.0
        self.save()

    def geocode_address(self, address):
        geolocator = Nominatim(user_agent="findoviodb")
        try:
            location = geolocator.geocode(address)
            if location:
                return location.latitude, location.longitude, 0  # Error Code 0 - Success
        except GeocoderTimedOut:
            return None, None, 2  # Error Code 2 - Geocoding Error - Timeout
        except GeocoderUnavailable:
            return None, None, 3  # Error Code 3 - Geocoding Error - Service Unavailable
        except GeocoderServiceError:
            return None, None, 4  # Error Code 4 - Other Geocoding Error
        return None, None, 1  # Error Code 1 - Geocoding Error

    def save(self, *args, **kwargs):
        if not self.pk:
            address = f"{self.address_street} {self.address_number}, {self.address_postal_code} {self.address_city}"
            longitude, latitude, error_code = self.geocode_address(address)

            if latitude is not None and longitude is not None:
                self.location = Point(longitude, latitude, srid=4326)
            else:
                error_code = 6  # Error Code 1 - Geocoding Error

            self.error_code = error_code

        super().save(*args, **kwargs)

class SalonImage(models.Model):
    salon_id = models.IntegerField()  # Pole przechowujące ID salonu
    image = models.ImageField(upload_to='salon_images', null=True)
    image_type = models.CharField(max_length=10)  # 'avatar' or 'gallery'

class SalonImageFinal(models.Model):
    salon_id = models.IntegerField()  # Pole przechowujące ID salonu
    image = models.ImageField(upload_to='salon_images', null=True)
    image_type = models.CharField(max_length=10)  # 'avatar' or 'gallery'


class FirebaseUsers(models.Model):
    firebase_name = models.CharField(max_length=40)
    firebase_email = models.CharField(max_length=80)
    firebase_uid = models.CharField(max_length=100, unique=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    avatar = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return self.name

class Category(models.Model):
    salon = models.ForeignKey(Salon, on_delete=models.CASCADE, related_name='categories', blank=True)
    name = models.CharField(max_length=100)
    is_available = models.BooleanField(default=True)

class Service(models.Model):
    salon = models.ForeignKey(Salon, on_delete=models.CASCADE, related_name='salon_categories', null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='services', null=True)
    title = models.CharField(max_length=101)
    description = models.TextField(max_length=200)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    duration_minutes = models.PositiveIntegerField(default='')
    duration_temp = models.DurationField(default=timedelta(minutes=30))
    is_available = models.BooleanField(default=True)

class Review(models.Model):
    salon = models.ForeignKey(Salon, on_delete=models.CASCADE, related_name='reviews')
    user_id = models.CharField(max_length=100)
    rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(max_length=500, default='')
    image_url = models.URLField(max_length=200, null=True, blank=True, default='')  # New image_url field
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

def get_default_date():
    return timezone.now().date()

class FixedOperatingHours(models.Model):
    salon = models.ForeignKey(Salon, on_delete=models.CASCADE)
    day_of_week = models.IntegerField()  # 0: Monday, 1: Tuesday, ..., 6: Sunday
    open_time = models.TimeField()
    close_time = models.TimeField()
    time_slot_length = models.IntegerField(default=20)  # Length of the time slot in minutes

    class Meta:
        unique_together = ("salon", "day_of_week")

    def generate_time_slots(self):
        delta = timedelta(minutes=self.time_slot_length)
        
        start_date = timezone.now().date()
        end_date = start_date + timedelta(days=30)
        
        current_date = start_date
        
        while current_date <= end_date:
            if current_date.weekday() == self.day_of_week:
                # Combine date and time to create datetime objects
                time_from = datetime.combine(current_date, self.open_time)
                time_to = datetime.combine(current_date, self.close_time)

                while time_from + delta <= time_to:
                    GeneratedTimeSlots.objects.create(
                        salon=self.salon,
                        date=current_date,
                        time_from=time_from.time(),
                        time_to=(time_from + delta).time(),
                    )
                    time_from += delta

            current_date += timedelta(days=1)

        return GeneratedTimeSlots.objects.filter(salon=self.salon).order_by('date', 'time_from')

    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  # Call the "real" save() method.
        self.generate_time_slots()

class UnFixedOperatingHours(models.Model):
    salon = models.ForeignKey(Salon, on_delete=models.CASCADE)
    date = models.DateField()
    open_time = models.TimeField()
    close_time = models.TimeField()
    time_slot_length = models.IntegerField(default=20)  # Length of the time slot in minutes

    class Meta:
        unique_together = ("salon", "date")
    
    def generate_time_slots(self):
        delta = timedelta(minutes=self.time_slot_length)
        
        # Combine date and time to create datetime objects
        time_from = datetime.combine(self.date, self.open_time)
        time_to = datetime.combine(self.date, self.close_time)

        while time_from + delta <= time_to:
            GeneratedTimeSlots.objects.create(
                salon=self.salon,
                date=self.date,
                time_from=time_from.time(),
                time_to=(time_from + delta).time(),
            )
            time_from += delta

        return GeneratedTimeSlots.objects.filter(salon=self.salon, date=self.date).order_by('time_from')
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  # Call the "real" save() method.
        self.generate_time_slots()

class GeneratedTimeSlots(models.Model):
    salon = models.ForeignKey(Salon, on_delete=models.CASCADE)
    date = models.DateField()
    time_from = models.TimeField()
    time_to = models.TimeField()
    is_available = models.BooleanField(default=True)

    class Meta:
        unique_together = ("salon", "date", "time_from", "time_to")
        indexes = [
            models.Index(fields=['salon'], name='salon_idx'),
        ]

class TempTimeSlots(models.Model):
    salon = models.ForeignKey(Salon, on_delete=models.CASCADE)
    date = models.DateField()
    time_from = models.TimeField()
    time_to = models.TimeField()
    is_available = models.BooleanField(default=True)

    class Meta:
        unique_together = ("salon", "date", "time_from", "time_to")

class Appointment(models.Model):
    STATUS_CHOICES = (
        ('P', 'Pending'),
        ('C', 'Confirmed'),
        ('F', 'Finished'),
        ('X', 'Cancelled'),
    )

    salon = models.ForeignKey(Salon, on_delete=models.CASCADE)
    customer = models.CharField(max_length=255)  # Assuming the customer is a User
    date_of_booking = models.DateField(blank=True)
    services = models.ManyToManyField(Service)
    comment = models.TextField(blank=True, null=True)
    total_amount = models.DecimalField(max_digits=6, decimal_places=2)
    status = models.CharField(choices=STATUS_CHOICES, default='X', max_length=22)
    created_at = models.DateTimeField(auto_now_add=True)
    timeslots = models.ManyToManyField(GeneratedTimeSlots)


class KeywordsCounter(models.Model):
    word = models.CharField(max_length=255, unique=True)
    count = models.IntegerField(default=1)

    def __str__(self):
        return self.word

class Advertisement(models.Model):
    banner_style = models.IntegerField(default=1, choices=[(i, str(i)) for i in range(1, 11)])
    promotion_level = models.IntegerField(default=1, choices=[(i, str(i)) for i in range(1, 4)])
    salon = models.ForeignKey('Salon', on_delete=models.CASCADE)
    Title_line_1 = models.CharField(max_length=30)
    Title_line_2 = models.CharField(max_length=50, blank=True)
    Text_line_1 = models.CharField(max_length=30)
    Text_line_2 = models.CharField(max_length=50, blank=True)
    Special_text = models.CharField(max_length=20, blank=True)
    Date_of_order = models.DateTimeField(default=timezone.now)
    Date_start = models.DateField()
    Date_end = models.DateField()
    promotion_price = models.FloatField()
    image = models.URLField()

    def __str__(self):
        return f"{self.Title_line_1} - {self.salon.name}"

class FindovioAdvertisement(models.Model):
    id = models.AutoField(primary_key=True)
    forceVisibility = models.BooleanField(default=False)
    url = models.URLField()
    title = models.CharField(max_length=100)  # Dodane pole tytułu
    content = models.TextField()  # Dodane pole treści (długi string)

    def __str__(self):
        return f"Advertisement {self.id}"
# {
#     "id": 1,
#     "forceVisibility": true,
#     "url": "http://185.180.204.182/reklama22014.png"
# }


class License(models.Model):
    LICENSE_CHOICES = (
        (0, 'Free'),
        (1, 'Pro'),
        (2, 'Premium'),
    )
    
    PLAN_CHOICES = (
        (0, 'Monthly'),
        (1, 'Annual'),
    )

    username = models.CharField(max_length=150, unique=True)
    kind_of_license = models.IntegerField(choices=LICENSE_CHOICES, default=0)
    is_active = models.BooleanField(default=True)
    plan_type = models.IntegerField(choices=PLAN_CHOICES, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.username} - {self.get_kind_of_license_display()}"

class Payment(models.Model):
    PAYMENT_CHOICES = (
        (0, 'Monthly'),
        (1, 'Annual'),
    )

    username = models.CharField(max_length=150)
    date = models.DateTimeField(auto_now_add=True)
    kind_of_license = models.IntegerField(choices=License.LICENSE_CHOICES)
    kind_of_payment = models.IntegerField(choices=PAYMENT_CHOICES)
    license = models.ForeignKey(License, related_name='payments', on_delete=models.CASCADE, default=0)

    def __str__(self):
        return f"{self.username} - {self.get_kind_of_license_display()} on {self.date}"