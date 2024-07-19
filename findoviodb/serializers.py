from datetime import timedelta
from django.db.models import Avg
from rest_framework import serializers
from .models import Salon, FirebaseUsers, Category, Service, Review, GeneratedTimeSlots, FixedOperatingHours, UnFixedOperatingHours, Appointment, KeywordsCounter, Advertisement, FindovioAdvertisement, SalonImageFinal, License, Payment

class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ('id', 'salon', 'category', 'title', 'description', 'price', 'duration_minutes', 'is_available')


class SalonImageSerializerFinal(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = SalonImageFinal
        fields = ('id', 'salon_id', 'image', 'image_type', 'image_url')

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image:
            return request.build_absolute_uri(obj.image.url)
        return None

class CategorySerializer(serializers.ModelSerializer):
    services = ServiceSerializer(many=True, required=False)
    

    class Meta:
        model = Category
        fields = ('id', 'salon', 'name', 'services', 'is_available')

    def create(self, validated_data):
        services_data = validated_data.pop('services', [])
        category_instance = Category.objects.create(**validated_data)

        for service_data in services_data:
            Service.objects.create(category=category_instance, **service_data)

        return category_instance
    
    def update(self, instance, validated_data):
        # Aktualizacja tylko pól name i is_available
        instance.name = validated_data.get('name', instance.name)
        instance.is_available = validated_data.get('is_available', instance.is_available)
        instance.save()

        return instance

class SalonSerializer(serializers.ModelSerializer):
    categories = CategorySerializer(many=True, required=False)
    review = serializers.SerializerMethodField()
    print('add')
    class Meta:
        model = Salon
        fields = ('id', 'name', 'address_city', 'address_postal_code', 'address_street', 'address_number', 'location',
                  'about', 'avatar', 'phone_number', 'distance_from_query', 'error_code', 'flutter_category', 'flutter_gender_type', 'categories', 'review', 'codes', 'email', 'gallery') 
    
    def get_review(self, obj):
        # Oblicz średnią ocenę dla salonu lub zwróć 0.0, jeśli brak ocen
        reviews = obj.reviews.all()
        if reviews.exists():
            return round(reviews.aggregate(Avg('rating'))['rating__avg'], 1)
        return 0.1
        
    def create(self, validated_data):
        categories_data = validated_data.pop('categories', [])
        salon = Salon.objects.create(**validated_data)

        for category_data in categories_data:
            services_data = category_data.pop('services', [])
            category = Category.objects.create(salon=salon, **category_data)

            for service_data in services_data:
                Service.objects.create(salon=salon, category=category, **service_data)

         # Create a license entry with the email as username
        try:
            # Create a license entry with the email as username
            license_instance = License.objects.create(
                username=validated_data['email'],
                kind_of_license=0,  # Default to free license
                is_active=True,
                plan_type=0  # Default to monthly plan
            )
            print('license created')

            # Create a default payment entry
            Payment.objects.create(
                username=validated_data['email'],
                kind_of_license=0,  # Default to free license
                kind_of_payment=0,  # Default to monthly payment
                license=license_instance
            )
            print('demo payment created')

        except Exception as e:
            print(f"An error occurred: {e}")
            # You may also want to delete the created salon if license creation fails
            salon.delete()
            raise serializers.ValidationError(f"An error occurred while creating license or payment: {e}")

        return salon


    def update(self, instance, validated_data):
        categories_data = validated_data.pop('categories', [])  # Default to empty list if 'categories' is missing
        instance.name = validated_data.get('name', instance.name)
        instance.address_city = validated_data.get('address_city', instance.address_city)
        instance.address_postal_code = validated_data.get('address_postal_code', instance.address_postal_code)
        instance.address_street = validated_data.get('address_street', instance.address_street)
        instance.address_number = validated_data.get('address_number', instance.address_number)
        instance.location = validated_data.get('location', instance.location)
        instance.about = validated_data.get('about', instance.about)
        instance.avatar = validated_data.get('avatar', instance.avatar)
        instance.phone_number = validated_data.get('phone_number', instance.phone_number)
        instance.distance_from_query = validated_data.get('distance_from_query', instance.distance_from_query)
        instance.error_code = validated_data.get('error_code', instance.error_code)
        instance.flutter_category = validated_data.get('flutter_category', instance.flutter_category)
        instance.flutter_gender_type = validated_data.get('flutter_gender_type', instance.flutter_gender_type)
        ('flutter_gender_type', instance.flutter_gender_type)
        instance.codes = validated_data.get('codes', instance.codes)
        instance.email = validated_data.get('email', instance.email)
        instance.gallery = validated_data.get('gallery', instance.gallery)
        instance.save()

        for category_data in categories_data:
            category_id = category_data.get('id', None)
            if category_id is None:
                services_data = category_data.pop('services', [])  # Default to empty list if 'services' is missing
                salon_instance = instance
                category = Category.objects.create(salon=salon_instance, **category_data)

                for service_data in services_data:
                    Service.objects.create(salon=instance, category=category, **service_data)
            else:
                try:
                    category = Category.objects.get(id=category_id, salon=instance)
                except Category.DoesNotExist:
                    continue

                category.name = category_data.get('name', category.name)
                category.save()

                for service_data in category_data.get('services', []):
                    service_id = service_data.get('id', None)
                    if service_id is None:
                        Service.objects.create(salon=instance, category=category, **service_data)
                    else:
                        try:
                            service = Service.objects.get(id=service_id, category=category)
                        except Service.DoesNotExist:
                            continue

                        service.title = service_data.get('title', service.title)
                        service.description = service_data.get('description', service.description)
                        service.price = service_data.get('price', service.price)
                        service.duration_minutes = service_data.get('duration_minutes', service.duration_minutes)
                        service.save()

        return instance


class FirebaseUsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = FirebaseUsers
        fields = '__all__'

class ReadOnlySalonSerializer(serializers.ModelSerializer):
    categories = CategorySerializer(many=True, read_only=True)
    review = serializers.SerializerMethodField() 
    class Meta:
        model = Salon
        fields = ('id','name', 'address_city', 'address_postal_code', 'address_street', 'address_number', 'location',
                  'about','avatar', 'phone_number', 'distance_from_query', 'error_code', 'flutter_category', 'flutter_gender_type', 'categories', 'review', 'codes', 'email', 'gallery')

    def get_review(self, obj):
        # Oblicz średnią ocenę dla salonu lub zwróć 0.0, jeśli brak ocen
        reviews = obj.reviews.all()
        if reviews.exists():
            return round(reviews.aggregate(Avg('rating'))['rating__avg'], 1)
        return 0.1
    
    def create(self, validated_data):
        categories_data = validated_data.pop('categories')
        salon = Salon.objects.create(**validated_data)

        for category_data in categories_data:
            services_data = category_data.pop('services')
            category = Category.objects.create(salon=salon, **category_data)

            for service_data in services_data:
                Service.objects.create(salon=salon, category=category, **service_data)

        return salon
    
class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ('id', 'salon', 'user_id', 'rating', 'comment', 'image_url', 'created_at', 'updated_at')
        
class FixedOperatingHoursSerializer(serializers.ModelSerializer):
    class Meta:
        model = FixedOperatingHours
        fields = '__all__'

    def to_internal_value(self, data):
        if isinstance(data.get('salon'), int):
            salon_id = data.pop('salon')
            data['salon'] = salon_id
        return super().to_internal_value(data)

class UnFixedOperatingHoursSerializer(serializers.ModelSerializer):
    class Meta:
        model = UnFixedOperatingHours
        fields = '__all__'

class GeneratedTimeSlotsSerializer(serializers.ModelSerializer):
    class Meta:
        model = GeneratedTimeSlots
        fields = ['id','salon', 'date', 'time_from', 'time_to', 'is_available']

from django.core.mail import send_mail

class AppointmentReadSerializer(serializers.ModelSerializer):
    services = ServiceSerializer(many=True)
    salon_name = serializers.SerializerMethodField()
    timeslots = GeneratedTimeSlotsSerializer(many=True)
    total_amount = serializers.DecimalField(max_digits=6, decimal_places=2, read_only=True)
    status = serializers.CharField(default='P', read_only=True)
    customer_object = serializers.SerializerMethodField()

    def get_customer_object(self, obj):
        try:
            # Sprawdź, czy istnieje użytkownik FirebaseUsers z odpowiednim firebase_uid
            firebase_user = FirebaseUsers.objects.get(firebase_uid=obj.customer)
            serializer = FirebaseUsersSerializer(firebase_user)
            return serializer.data
        except FirebaseUsers.DoesNotExist:
            return None

    class Meta:
        model = Appointment
        fields = ['id', 'salon', 'salon_name', 'customer', 'customer_object', 'date_of_booking', 'services', 'total_amount','comment', 'status', 'created_at', 'timeslots']
        read_only_fields = ['total_amount', 'status', 'created_at', 'date_of_booking']

    def get_salon_name(self, obj):
        return obj.salon.name if obj.salon else None
    
    def create(self, validated_data):
        services = validated_data.pop('services')
        timeslots = validated_data.pop('timeslots')
        print
        
        salon = validated_data.get('salon')
        customer = validated_data.get('customer')
        comment = validated_data.get('comment')

        # Checking if the salon ID exists
        if not Salon.objects.filter(id=salon.id).exists():
            print("The specified salon does not exist.")
            raise serializers.ValidationError("The specified salon does not exist.")

        # Checking if the services correspond to the correct salon
        if not all(service.salon.id == salon.id for service in services):
            print("One or more services do not belong to the specified salon.")
            raise serializers.ValidationError("One or more services do not belong to the specified salon.")

        # Checking if the timeslots correspond to the correct salon
        if not all(timeslot.salon.id == salon.id for timeslot in timeslots):
            print("One or more timeslots do not belong to the specified salon.")
            raise serializers.ValidationError("One or more timeslots do not belong to the specified salon.")

        # Checking if all timeslots are available
        if not all(timeslot.is_available for timeslot in timeslots):
            print("One or more of the specified timeslots are not available.")
            raise serializers.ValidationError("One or more of the specified timeslots are not available.")
        

        # Calculate total duration and price
        total_duration = timedelta()
        total_amount = 0
        for service in services:
            total_duration += service.duration_temp
            total_amount += service.price
        
        print('total_duration', total_duration)

        # total_duration = sum(service.duration_temp for service in services)
        # total_amount = sum(service.price for service in services)

        # Get the slot length from FixedOperatingHours or UnFixedOperatingHours
        try:
            fixed_operating_hours = FixedOperatingHours.objects.filter(salon=salon).first()
            if fixed_operating_hours:
                slot_length = fixed_operating_hours.time_slot_length
                print("Slot Length:", slot_length)
            else:
                print("No FixedOperatingHours found for the salon")
        except FixedOperatingHours.DoesNotExist:
            print("FixedOperatingHours not found")
            slot_length = None


        # Calculate how many time slots are needed
        total_timeslots_needed = int(total_duration.total_seconds() / 60) // slot_length
        print('total timeslots needed',total_timeslots_needed)
        print('len timeslots',len(timeslots))
        print('timeslots', timeslots)
        if total_duration % timedelta(minutes=slot_length):
            total_timeslots_needed += 1

        # Checking if calculated amount of timeslots corresponds to given timeslots in request
        if total_timeslots_needed != len(timeslots):
            raise serializers.ValidationError("The number of timeslots ({}) does not match the total duration of the services ({} minutes), ({}) - timeslots_needed.".format(len(timeslots), total_duration.total_seconds() / 60, total_timeslots_needed))


        # Check if given timeslots are in one day
        if len(set(timeslot.date for timeslot in timeslots)) != 1:
            raise serializers.ValidationError("All timeslots must be on the same day.")

        # check if end time of all given timeslots or timeslot doesn't exceed operating hours time
        timeslots_sorted = sorted(timeslots, key=lambda x: x.time_from)
        last_timeslot_end_time = timeslots_sorted[-1].time_from
        try:
            closing_time = FixedOperatingHours.objects.get(salon=salon, day_of_week=timeslots_sorted[0].date.weekday()).close_time
        except FixedOperatingHours.DoesNotExist:
            closing_time = UnFixedOperatingHours.objects.get(salon=salon, date=timeslots_sorted[0].date).close_time
        if last_timeslot_end_time > closing_time:
            raise serializers.ValidationError("The end time of the appointment exceeds the operating hours of the salon.")
        
        first_timeslot = timeslots[0]  # Assuming timeslots list is not empty
        date_of_booking = first_timeslot.date

        # At this point, all the checks are passed, we can now create the appointment
        appointment = Appointment.objects.create(
            salon=salon,
            customer=customer,
            comment=comment,
            total_amount=total_amount,
            status='P',  # 'P' for Pending
            date_of_booking=date_of_booking,
        )

        # Attach the services and timeslots to the appointment
        for service in services:
            appointment.services.add(service)
        for timeslot in timeslots:
            timeslot.is_available = False
            timeslot.save()
            appointment.timeslots.add(timeslot)

        print(services[0].title)

        try:
            firebase_user = FirebaseUsers.objects.get(firebase_uid=customer)
            send_mail(
                'Appointment Confirmation',
                f'Hello {firebase_user.firebase_name},\n\nYour appointment has been successfully booked at {salon.name}.\n\nThank you!',
                'your-email@example.com',
                [firebase_user.firebase_email],
                fail_silently=False,
            )
        except Exception as e:
            # Log the error
            print(f'Failed to send email: {str(e)}')
            # You can also raise an error if you want to inform the user
            raise serializers.ValidationError('Failed to send confirmation email.')
        return appointment
    
    # {
    # "salon": 22,
    # "customer": "Damianek",
    # "services": [49],
    # "comment": "I would like a haircut and a shave.",
    # "timeslots": [33,34,35]
    # }

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags


class AppointmentWriteSerializer(serializers.ModelSerializer):
    services = serializers.PrimaryKeyRelatedField(many=True, queryset=Service.objects.all())
    timeslots = serializers.PrimaryKeyRelatedField(many=True, queryset=GeneratedTimeSlots.objects.all())
    total_amount = serializers.DecimalField(max_digits=6, decimal_places=2, read_only=True)
    status = serializers.CharField(default='P', read_only=True)

    class Meta:
        model = Appointment
        fields = ['id', 'salon', 'customer', 'date_of_booking', 'services', 'total_amount','comment', 'status', 'created_at', 'timeslots']
        read_only_fields = ['total_amount', 'status', 'created_at', 'date_of_booking']

    def convert_duration(self, duration):
        # Konwersja timedelta na liczbę minut
        total_minutes = int(duration.total_seconds() // 60)
        hours = total_minutes // 60
        minutes = total_minutes % 60
        if hours > 0:
            return f"{hours} godzin{'a' if hours > 1 else ''} i {minutes} minut"
        else:
            return f"{minutes} minut"


    def send_confirmation_email(self, customer, appointment, salon_id, services):
        firebase_user = FirebaseUsers.objects.get(firebase_uid=customer)
        salon = Salon.objects.get(id=salon_id)
        # Przygotowanie zawartości emaila
        date = appointment.date_of_booking.strftime('%Y-%m-%d')
        subject = f'Potwierdzenie wizyty - [{date}]'
        from_email = f'Findovio | Rezerwacja {salon.name} <rezerwacje@findovio.nl>'
        to_email = firebase_user.firebase_email
        to_email_biz = salon.email
        bcc_email = ['damian@findovio.nl']
        # Łączenie pełnego adresu salonu
        salon_address = f"{salon.address_street} {salon.address_number}, {salon.address_postal_code} {salon.address_city}"
        salon_google_address = f"https://www.google.com/maps/place/{salon.address_city}, {salon.address_postal_code}, {salon.address_street} {salon.address_number}"

        total_duration_minutes = sum(service.duration_minutes for service in services)
        
        html_content = render_to_string('appointment_pending_template_client.html', {
            'customer_name': firebase_user.firebase_name,
            'appointment_date': appointment.date_of_booking.strftime('%Y-%m-%d'),
            'appointment_time': appointment.timeslots.first().time_from.strftime('%H:%M'),
            'salon_name': salon.name,
            'salon_address': salon_address,
            'services': services,
            'duration': total_duration_minutes,
            'total_cost': appointment.total_amount,
            'appointment_id': appointment.id,
            'salon_google_address': salon_google_address
        })

        html_content_to_biz = render_to_string('appointment_pending_template_biz.html', {
            'customer_name': firebase_user.firebase_name,
            'appointment_date': appointment.date_of_booking.strftime('%Y-%m-%d'),
            'appointment_time': appointment.timeslots.first().time_from.strftime('%H:%M'),
            'salon_name': salon.name,
            'salon_address': salon_address,
            'services': services,
            'duration': total_duration_minutes,
            'total_cost': appointment.total_amount,
            'appointment_id': appointment.id,
            'salon_google_address': salon_google_address
        })
    
        text_content = strip_tags(html_content)
        text_content_to_biz = strip_tags(html_content_to_biz)
        
        try:
            print('sending')
            msg = EmailMultiAlternatives(subject, text_content, from_email, [to_email], bcc=bcc_email)
            msg_biz = EmailMultiAlternatives(subject, text_content_to_biz, from_email, [to_email_biz], bcc=bcc_email)
            msg.attach_alternative(html_content, "text/html")
            msg_biz.attach_alternative(html_content_to_biz, "text/html")
            try:
                msg.send()
            except Exception as e:
                print(f"Error sending client email: {e}")
            try:
                msg_biz.send()
                print('sent')
            except Exception as e:
                print(f"Error sending biz email: {e}")
                
        except Exception as e:
            print(f"Error sending email: {e}")



    def create(self, validated_data):
        services = validated_data.pop('services')
        timeslots = validated_data.pop('timeslots')
        
        salon = validated_data.get('salon')
        customer = validated_data.get('customer')
        comment = validated_data.get('comment')
        
        # Checking if the salon ID exists
        if not Salon.objects.filter(id=salon.id).exists():
            print("The specified salon does not exist.")
            raise serializers.ValidationError("The specified salon does not exist.")

        # Checking if the services correspond to the correct salon
        if not all(service.salon.id == salon.id for service in services):
            print("One or more services do not belong to the specified salon.")
            raise serializers.ValidationError("One or more services do not belong to the specified salon.")

        # Checking if the timeslots correspond to the correct salon
        if not all(timeslot.salon.id == salon.id for timeslot in timeslots):
            print("One or more timeslots do not belong to the specified salon.")
            raise serializers.ValidationError("One or more timeslots do not belong to the specified salon.")

        # Checking if all timeslots are available
        if not all(timeslot.is_available for timeslot in timeslots):
            print("One or more of the specified timeslots are not available.")
            raise serializers.ValidationError("One or more of the specified timeslots are not available.")
        

        # Calculate total duration and price
        total_duration = timedelta()
        total_amount = 0
        for service in services:
            total_duration += service.duration_temp
            total_amount += service.price
        
        print('total_duration', total_duration)

        # total_duration = sum(service.duration_temp for service in services)
        # total_amount = sum(service.price for service in services)

        # Get the slot length from FixedOperatingHours or UnFixedOperatingHours
        try:
            fixed_operating_hours = FixedOperatingHours.objects.filter(salon=salon).first()
            if fixed_operating_hours:
                slot_length = fixed_operating_hours.time_slot_length
                print("Slot Length:", slot_length)
            else:
                print("No FixedOperatingHours found for the salon")
        except FixedOperatingHours.DoesNotExist:
            print("FixedOperatingHours not found")
            slot_length = None


        # Calculate how many time slots are needed
        total_timeslots_needed = int(total_duration.total_seconds() / 60) // slot_length
        print('total timeslots needed',total_timeslots_needed)
        print('len timeslots',len(timeslots))
        print('timeslots', timeslots)
        if total_duration % timedelta(minutes=slot_length):
            total_timeslots_needed += 1
        print('sraka')
        print(total_timeslots_needed)
        print(len(timeslots))
        # Checking if calculated amount of timeslots corresponds to given timeslots in request
        # [total_timeslots_needed] - [len(timeslots)] > [ 3 ]
        # [ 3 ] - to ile timeslotów po godzinie zamknięcia może jeszcze obsługiwać klientów
        if (total_timeslots_needed - len(timeslots) > 3):
            raise serializers.ValidationError("The number of timeslots ({}) does not match the total duration of the services ({} minutes), ({}) - timeslots_needed.".format(len(timeslots), total_duration.total_seconds() / 60, total_timeslots_needed))

        print("tu sraka")
        # Check if given timeslots are in one day
        if len(set(timeslot.date for timeslot in timeslots)) != 1:
            raise serializers.ValidationError("All timeslots must be on the same day.")
        print("tu sraka")
        # check if end time of all given timeslots or timeslot doesn't exceed operating hours time
        timeslots_sorted = sorted(timeslots, key=lambda x: x.time_from)
        print("timeslots_sorted: ", timeslots_sorted)
        last_timeslot_end_time = timeslots_sorted[-1].time_from
        
        print(last_timeslot_end_time)
        try:
            print("try 1")
            # print("fixed: ", FixedOperatingHours.objects.get())
            print("Salon: ", salon)
            print("closing time: ", FixedOperatingHours.objects.get(salon=salon, day_of_week=timeslots_sorted[0].date.weekday()))
            closing_time = FixedOperatingHours.objects.get(salon=salon, day_of_week=timeslots_sorted[0].date.weekday()).close_time
            print("try 2")
        except FixedOperatingHours.DoesNotExist:
            print("tu sraka2")
            closing_time = UnFixedOperatingHours.objects.get(salon=salon, date=timeslots_sorted[0].date).close_time

        print("tu sraka")
        if last_timeslot_end_time > closing_time:
            raise serializers.ValidationError("The end time of the appointment exceeds the operating hours of the salon.")
        print("tu sraka")
        first_timeslot = timeslots[0]  # Assuming timeslots list is not empty
        date_of_booking = first_timeslot.date
        print('chuj')
        # At this point, all the checks are passed, we can now create the appointment
        appointment = Appointment.objects.create(
            salon=salon,
            customer=customer,
            comment=comment,
            total_amount=total_amount,
            status='P',  # 'P' for Pending
            date_of_booking=date_of_booking,
        )

        # Attach the services and timeslots to the appointment
        for service in services:
            appointment.services.add(service)
        for timeslot in timeslots:
            timeslot.is_available = False
            timeslot.save()
            appointment.timeslots.add(timeslot)

        print(services[0].title)
        print('sending mail')
        try:
            self.send_confirmation_email(customer, appointment, salon.id, services)
            print('mail sent')
        except Exception as e:
            print(f"Error sending email: {e}")
        return appointment
    
    # {
    # "salon": 22,
    # "customer": "Damianek",
    # "services": [49],
    # "comment": "I would like a haircut and a shave.",
    # "timeslots": [33,34,35]
    # }

class KeywordsCounterSerializer(serializers.ModelSerializer):
    class Meta:
        model = KeywordsCounter
        fields = ('word', 'count')

class AvatarBySalonNameSerializer(serializers.ModelSerializer):
    avatar = serializers.URLField(source='salon__avatar', read_only=True)

    class Meta:
        model = Salon
        fields = ['avatar']

    def to_representation(self, instance):
        if 'salon_name' in self.context:
            salon_name = self.context['salon_name']
            salon = Salon.objects.filter(name=salon_name).first()
            if salon:
                return super().to_representation(salon)
        
        return super().to_representation(instance)
    
class AdvertisementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Advertisement
        fields = ('id', 'banner_style', 'promotion_level', 'salon', 'Title_line_1', 'Title_line_2',
                  'Text_line_1', 'Text_line_2', 'Special_text', 'Date_of_order', 'Date_start',
                  'Date_end', 'promotion_price', 'image')

class FindovioAdvertisementSerializer(serializers.ModelSerializer):
    class Meta:
        model = FindovioAdvertisement
        fields = ('id', 'forceVisibility', 'url', 'title', 'content')

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ('username', 'date', 'kind_of_license', 'kind_of_payment')

class LicenseSerializer(serializers.ModelSerializer):
    payments = PaymentSerializer(many=True, read_only=True)

    class Meta:
        model = License
        fields = ('username', 'kind_of_license', 'is_active', 'plan_type', 'created_at', 'payments')


class SalonSearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Salon
        fields = ['name', 'address_city', 'address_street', 'address_number', 'avatar']

class ServiceSearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ['title']

class CategorySearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['name']