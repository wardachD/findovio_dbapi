# Imports

# Firebase
# [Tokenization] only
from firebase_admin import auth

# Image converting
from PIL import Image
from io import BytesIO

# rest_framework
from rest_framework import viewsets, status, filters, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.generics import ListAPIView
from rest_framework.parsers import MultiPartParser
from rest_framework.exceptions import NotFound

# django imports
from urllib.parse import quote
from django.http import Http404
from django.db.models import Count, F
from django.db.models.functions import Lower
from django.http import JsonResponse, HttpResponseNotFound, HttpResponseServerError
from django_filters.rest_framework import DjangoFilterBackend
from django.core.files.base import ContentFile

import json
# Models
from .models import Salon, SalonImage, FirebaseUsers, Category, Service, Review, FixedOperatingHours, UnFixedOperatingHours, GeneratedTimeSlots, Appointment, KeywordsCounter, Advertisement, FindovioAdvertisement, Payment, License

# Serializers
from .serializers import SalonSerializer, FirebaseUsersSerializer, AppointmentReadSerializer, AppointmentWriteSerializer, ReadOnlySalonSerializer, ServiceSerializer, CategorySerializer, ReviewSerializer, FixedOperatingHoursSerializer, GeneratedTimeSlotsSerializer, UnFixedOperatingHoursSerializer, KeywordsCounterSerializer, AvatarBySalonNameSerializer, AdvertisementSerializer, FindovioAdvertisementSerializer, SalonImageSerializerFinal, SalonImageFinal, LicenseSerializer, PaymentSerializer, SalonSearchSerializer, ServiceSearchSerializer, CategorySearchSerializer

# Functions
# [search]
from .search import search_salons, search_by_keywords, search_by_address_radius


############ [ + ] token secured
class FirebaseTokenVerificationMixin:
    def verify_firebase_token(self, id_token):
        try:
            decoded_token = auth.verify_id_token(id_token)
            return decoded_token
        except auth.InvalidIdTokenError:
            return status.HTTP_401_UNAUTHORIZED

############ [ + ] token secured
class SalonViewSet(FirebaseTokenVerificationMixin, viewsets.ModelViewSet):
    queryset = Salon.objects.all()
    print('salonviewset')
     # Method to verify token from request headers
    def verify_token_from_request(self, request):
        authorization_header = request.headers.get('Authorization')
        if authorization_header and authorization_header.startswith('Bearer '):
            token = authorization_header.split(' ')[1]
            decoded_token = self.verify_firebase_token(token)
            return decoded_token
        return None
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ReadOnlySalonSerializer
        return SalonSerializer
    
     # Override the list method (GET)
    def list(self, request, *args, **kwargs):
        print(1)
        # decoded_token = self.verify_token_from_request(request)
        # if not decoded_token:
        #     return Response({'error': 'Invalid or expired token'}, status=status.HTTP_401_UNAUTHORIZED)
        return super().list(request, *args, **kwargs)

    # Override the create method (POST)
    def create(self, request, *args, **kwargs):
        print(2)
        # decoded_token = self.verify_token_from_request(request)
        # if not decoded_token:
        #     return Response({'error': 'Invalid or expired token'}, status=status.HTTP_401_UNAUTHORIZED)
        # print(request)
        return super().create(request, *args, **kwargs)

    # Override the retrieve method (GET single object)
    def retrieve(self, request, *args, **kwargs):
        # decoded_token = self.verify_token_from_request(request)
        # if not decoded_token:
        #     return Response({'error': 'Invalid or expired token'}, status=status.HTTP_401_UNAUTHORIZED)
        return super().retrieve(request, *args, **kwargs)
        

    # Override the update method (PUT)
    def update(self, request, *args, **kwargs):
        # print(4)
        # decoded_token = self.verify_token_from_request(request)
        # if not decoded_token:
        #     return Response({'error': 'Invalid or expired token'}, status=status.HTTP_401_UNAUTHORIZED)
        return super().update(request, *args, **kwargs)

    # Override the partial_update method (PATCH)
    def partial_update(self, request, *args, **kwargs):
        print(5)
        decoded_token = self.verify_token_from_request(request)
        if not decoded_token:
            return Response({'error': 'Invalid or expired token'}, status=status.HTTP_401_UNAUTHORIZED)
        return super().partial_update(request, *args, **kwargs)

    # Override the destroy method (DELETE)
    def destroy(self, request, *args, **kwargs):
        print(6)
        decoded_token = self.verify_token_from_request(request)
        if not decoded_token:
            return Response({'error': 'Invalid or expired token'}, status=status.HTTP_401_UNAUTHORIZED)
        return super().destroy(request, *args, **kwargs)

############ [ + ] token secured   # Import FirebaseTokenVerificationMixin from your module

class SalonGetView(FirebaseTokenVerificationMixin, generics.ListAPIView):
    serializer_class = SalonSerializer

    def verify_token_from_request(self, request):
        authorization_header = request.headers.get('Authorization')
        if authorization_header and authorization_header.startswith('Bearer '):
            token = authorization_header.split(' ')[1]
            decoded_token = self.verify_firebase_token(token)
            return decoded_token
        return None

    def get_queryset(self):
        # decoded_token = self.verify_token_from_request(self.request)
        # if not decoded_token:
        #     # If token verification fails, return an empty queryset
        #     return Salon.objects.none()
        email = self.request.query_params.get('email', None)
        if email:
            print(email)
            return Salon.objects.filter(email=email)
        else:
            return Salon.objects.none()

    def get(self, request, *args, **kwargs):
        try:
            # decoded_token = self.verify_token_from_request(request)
            # if not decoded_token:
            #     return Response({'detail': 'Token verification failed'}, status=status.HTTP_401_UNAUTHORIZED)
            queryset = self.get_queryset()
            if queryset.exists():
                serializer = self.get_serializer(queryset, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response({'detail': 'No salons found for the provided email'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# class FirebaseUsersViewSet(FirebaseTokenVerificationMixin, viewsets.ModelViewSet): 
#     queryset = FirebaseUsers.objects.all()
#     serializer_class = FirebaseUsersSerializer

#     def patch(self, request, pk):
#         print('ver1')
#         try:
#             # Sprawdź czy nagłówek Authorization zawiera poprawny token
#             authorization_header = request.headers.get('Authorization')
#             if authorization_header and authorization_header.startswith('Bearer '):
#                 # Podziel nagłówek i pobierz sam token
#                 token = authorization_header.split(' ')[1]

#                 # Weryfikuj token Firebase
#                 decoded_token = self.verify_firebase_token(token)
#                 if not decoded_token:
#                     return Response({'error': 'Invalid or expired token'}, status=status.HTTP_401_UNAUTHORIZED)
#             else:
#                 return Response({'error': 'Unauthorized. Token missing or invalid'}, status=status.HTTP_401_UNAUTHORIZED)

#             # Jeśli token jest prawidłowy, wykonaj zwykłą logikę aktualizacji obiektu FirebaseUsers
#             instance = FirebaseUsers.objects.get(pk=pk)
#             serializer = FirebaseUsersSerializer(instance, data=request.data, partial=True)
#             if serializer.is_valid():
#                 serializer.save()
#                 return Response(serializer.data, status=status.HTTP_200_OK)
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#         except FirebaseUsers.DoesNotExist:
#             return Response({"error": "Object not found"}, status=status.HTTP_404_NOT_FOUND)

############ [ + ] token secured
class FirebaseUsersViewSet(FirebaseTokenVerificationMixin, viewsets.ModelViewSet): 
    queryset = FirebaseUsers.objects.all()
    serializer_class = FirebaseUsersSerializer

    # Method to verify token from request headers
    def verify_token_from_request(self, request):
        authorization_header = request.headers.get('Authorization')
        if authorization_header and authorization_header.startswith('Bearer '):
            token = authorization_header.split(' ')[1]
            decoded_token = self.verify_firebase_token(token)
            return decoded_token
        return None
    
    def create(self, request, *args, **kwargs):
        decoded_token = self.verify_token_from_request(request)
        print('this one')
        if not decoded_token:
            return Response({'error': 'Invalid or expired token'}, status=status.HTTP_401_UNAUTHORIZED)

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Method to handle GET request
    def retrieve(self, request, *args, **kwargs):
        decoded_token = self.verify_token_from_request(request)
        print('ciach')
        if not decoded_token:
            return Response({'error': 'Invalid or expired token'}, status=status.HTTP_401_UNAUTHORIZED)
        return super().list(request, *args, **kwargs)
        

    # Method to handle DELETE request
    def destroy(self, request, *args, **kwargs):
        decoded_token = self.verify_token_from_request(request)
        if not decoded_token:
            return Response({'error': 'Invalid or expired token'}, status=status.HTTP_401_UNAUTHORIZED)
        
        return super().destroy(request, *args, **kwargs)

    # Your existing method to update Firebase user
    @action(detail=True, methods=['patch'])
    def update_firebase_user(self, request, pk=None):
        try:
            decoded_token = self.verify_token_from_request(request)
            if not decoded_token:
                return Response({'error': 'Invalid or expired token'}, status=status.HTTP_401_UNAUTHORIZED)
            
            instance = self.get_object()
            serializer = FirebaseUsersSerializer(instance, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except FirebaseUsers.DoesNotExist:
            return Response({"error": "Object not found"}, status=status.HTTP_404_NOT_FOUND)

############ [ + ] token secured
class FirebaseUserDetailView(FirebaseTokenVerificationMixin, APIView):
    def get(self, request, firebase_uid):
        try:
            # authorization_header = request.headers.get('Authorization')
            # if authorization_header and authorization_header.startswith('Bearer '):
            #     # Podziel nagłówek i pobierz sam token
            #     token = authorization_header.split(' ')[1]

            #     # Weryfikuj token Firebase
            #     decoded_token = self.verify_firebase_token(token)
            #     if not decoded_token:
            #         return Response({'error': 'Invalid or expired token'}, status=status.HTTP_401_UNAUTHORIZED)
            # else:
            #     return Response({'error': 'Unauthorized. Token missing or invalid'}, status=status.HTTP_401_UNAUTHORIZED)
            user = FirebaseUsers.objects.get(firebase_uid=firebase_uid)
            serializer = FirebaseUsersSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except FirebaseUsers.DoesNotExist:
            return Response({'message': 'User not found for Firebase UID: ' + firebase_uid}, status=status.HTTP_404_NOT_FOUND)
        
    def patch(self, request, pk):
        try:
            # Sprawdź czy nagłówek Authorization zawiera poprawny token
            authorization_header = request.headers.get('Authorization')
            if authorization_header and authorization_header.startswith('Bearer '):
                # Podziel nagłówek i pobierz sam token
                token = authorization_header.split(' ')[1]

                # Weryfikuj token Firebase
                decoded_token = self.verify_firebase_token(token)
                if not decoded_token:
                    return Response({'error': 'Invalid or expired token'}, status=status.HTTP_401_UNAUTHORIZED)
            else:
                return Response({'error': 'Unauthorized. Token missing or invalid'}, status=status.HTTP_401_UNAUTHORIZED)

            # Jeśli token jest prawidłowy, wykonaj zwykłą logikę aktualizacji obiektu FirebaseUsers
            instance = FirebaseUsers.objects.get(pk=pk)
            serializer = FirebaseUsersSerializer(instance, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except FirebaseUsers.DoesNotExist:
            return Response({"error": "Object not found"}, status=status.HTTP_404_NOT_FOUND)

############ [ + ] token secured
class CategoryViewSet(FirebaseTokenVerificationMixin, viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    print('1')

    def list(self, request, *args, **kwargs):
        print('list')
        try:
            # Pobierz token z nagłówka 'Authorization'
            authorization_header = request.headers.get('Authorization')

            # Sprawdź czy nagłówek istnieje i czy zawiera token
            if authorization_header and authorization_header.startswith('Bearer '):
                # Podziel nagłówek i pobierz sam token
                token = authorization_header.split(' ')[1]

                # Weryfikuj token Firebase
                decoded_token = self.verify_firebase_token(token)
                if not decoded_token:
                    return Response({'error': 'Invalid or expired token'}, status=status.HTTP_401_UNAUTHORIZED)

                # Token zweryfikowany, kontynuuj
                return super().list(request, *args, **kwargs)
            else:
                # Jeśli nagłówek 'Authorization' nie istnieje lub nie zawiera tokenu, zwróć błąd
                return Response({'error': 'Unauthorized. Token missing or invalid'}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            # Obsłuż inne wyjątki
            print(f'Error: {e}')
            return Response({'error': 'Internal Server Error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def create(self, request, *args, **kwargs):
        try:
            categories_data = request.data
            created_categories = []

            for category_data in categories_data:
                serializer = self.get_serializer(data=category_data)
                if serializer.is_valid():
                    serializer.save()
                    created_categories.append(serializer.data)
                else:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            return Response(created_categories, status=status.HTTP_201_CREATED)

        except Exception as e:
            # Obsłuż błędy, jeśli wystąpią
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def partial_update(self, request, *args, **kwargs):
        try:
            print('update')
            
            authorization_header = request.headers.get('Authorization')

            # Sprawdź czy nagłówek istnieje i czy zawiera token
            if authorization_header and authorization_header.startswith('Bearer '):
                # Podziel nagłówek i pobierz sam token
                token = authorization_header.split(' ')[1]

                # # Weryfikuj token Firebase
                decoded_token = self.verify_firebase_token(token)
                if not decoded_token:
                    return Response({'error': 'Invalid or expired token'}, status=status.HTTP_401_UNAUTHORIZED)
                
                partial = kwargs.pop('partial', False)
                instance = self.get_object()
                serializer = self.get_serializer(instance, data=request.data, partial=partial)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                return Response(serializer.data)
            
            else:
                # Jeśli nagłówek 'Authorization' nie istnieje lub nie zawiera tokenu, zwróć błąd
                return Response({'error': 'Unauthorized. Token missing or invalid'}, status=status.HTTP_401_UNAUTHORIZED)
            
        except Exception as e:
            print(f'Error updating category: {e}')
            return Response({'error': 'Internal Server Error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def destroy(self, request, *args, **kwargs):
        try:
            # Pobierz token z nagłówka 'Authorization'
            authorization_header = request.headers.get('Authorization')

            # Sprawdź czy nagłówek istnieje i czy zawiera token
            if authorization_header and authorization_header.startswith('Bearer '):
                # Podziel nagłówek i pobierz sam token
                token = authorization_header.split(' ')[1]

                # Weryfikuj token Firebase
                decoded_token = self.verify_firebase_token(token)
                if not decoded_token:
                    return Response({'error': 'Invalid or expired token'}, status=status.HTTP_401_UNAUTHORIZED)

                # Token zweryfikowany, kontynuuj
                instance = self.get_object()
                self.perform_destroy(instance)
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                # Jeśli nagłówek 'Authorization' nie istnieje lub nie zawiera tokenu, zwróć błąd
                return Response({'error': 'Unauthorized. Token missing or invalid'}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            print(f'Error deleting category: {e}')
            return Response({'error': 'Internal Server Error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# class CategoryAPIView(FirebaseTokenVerificationMixin, APIView):
#     queryset = Category.objects.all()
#     serializer_class = CategorySerializer()
#     print('1')

#     def get(self, request, pk=None):
#         print('egt')
#         if pk is not None:
#             try:
#                 instance = Category.objects.get(pk=pk)
#                 serializer = CategorySerializer(instance)
#                 return Response(serializer.data)
#             except Category.DoesNotExist:
#                 return Response({'error': 'Category not found'}, status=status.HTTP_404_NOT_FOUND)
#         else:
#             queryset = Category.objects.all()
#             serializer = CategorySerializer(queryset, many=True)
#             return Response(serializer.data)

#     def post(self, request):
#         print('post')
#         serializer = CategorySerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     def patch(self, request, pk):
#         print('patch')
#         try:
#             print('patch')
#             instance = Category.objects.get(pk=pk)
#             serializer = CategorySerializer(instance, data=request.data, partial=True)
#             if serializer.is_valid(raise_exception=True):
#                 serializer.save()
#                 return Response(serializer.data)
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#         except Category.DoesNotExist:
#             return Response({'error': 'Category not found'}, status=status.HTTP_404_NOT_FOUND)

#     def delete(self, request, pk):
#         print('delete')
#         try:
#             instance = Category.objects.get(pk=pk)
#             instance.delete()
#             return Response(status=status.HTTP_204_NO_CONTENT)
#         except Category.DoesNotExist:
#             return Response({'error': 'Category not found'}, status=status.HTTP_404_NOT_FOUND)


############ [ + ] token secured
class ServiceViewSet(FirebaseTokenVerificationMixin, viewsets.ModelViewSet):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer

    def list(self, request, *args, **kwargs):
        try:
            # Pobierz token z nagłówka 'Authorization'
            authorization_header = request.headers.get('Authorization')

            # Sprawdź czy nagłówek istnieje i czy zawiera token
            if authorization_header and authorization_header.startswith('Bearer '):
                # Podziel nagłówek i pobierz sam token
                token = authorization_header.split(' ')[1]

                # Weryfikuj token Firebase
                decoded_token = self.verify_firebase_token(token)
                if not decoded_token:
                    return Response({'error': 'Invalid or expired token'}, status=status.HTTP_401_UNAUTHORIZED)

                # Token zweryfikowany, kontynuuj
                return super().list(request, *args, **kwargs)
            else:
                # Jeśli nagłówek 'Authorization' nie istnieje lub nie zawiera tokenu, zwróć błąd
                return Response({'error': 'Unauthorized. Token missing or invalid'}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            # Obsłuż inne wyjątki
            print(f'Error: {e}')
            return Response({'error': 'Internal Server Error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class SalonServiceListView(APIView):
    def get(self, request, salon_id, format=None):
        services = Service.objects.filter(salon_id=salon_id)
        serializer = ServiceSerializer(services, many=True)
        return Response(serializer.data)
    
    

# [NO NEED] token secured
class SalonSearchAPIView(APIView):
    def get(self, request):
        keywords = request.query_params.get('keywords', '')
        address = request.query_params.get('address', '')
        # radius = request.query_params.get('radius', '')
        print("search salon [xdfxdf]")
        # Warunek sprawdzający, czy przynajmniej jeden parametr wyszukiwania jest podany
        if not keywords and not address:
            print('not keywords and not address:')
            salons = Salon.objects.all()
        # elif address and not keywords and category:
        #     print('with category address and radius and not keywords and category:')
        #     salons = search_salons(address)
        # elif address and not keywords:
        #     print('without category address and radius and not keywords:')
        #     salons = search_salons(keywords, address)
        # elif keywords and address and category:
        #     print('with category keywords and address and radius and category:')
        #     salons = search_salons(keywords, address)
        # elif keywords and address:
        #     print('without category keywords and address and radius:')
        #     salons = search_salons(keywords, address)
        else:
            # Jeżeli nie podano żadnego parametru, zwracamy wszystkie salony
            print("search salon [xdfxdf]")
            salons = search_salons(keywords, address)

        # Używamy JsonResponse, aby zwrócić dane JSON z poprawnym nagłówkiem Content-Type
        print('makejson')
        try:
            data = ReadOnlySalonSerializer(salons, many=True)
            print('done')
        except Exception as e:
            print(e)
        return Response(data.data, status=status.HTTP_200_OK)

############ [ + ] token secured
class ReviewViewSet(FirebaseTokenVerificationMixin, viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer

    def verify_token_from_request(self, request):
        authorization_header = request.headers.get('Authorization')
        if authorization_header and authorization_header.startswith('Bearer '):
            token = authorization_header.split(' ')[1]
            decoded_token = self.verify_firebase_token(token)
            return decoded_token
        return None

    def create(self, request, *args, **kwargs):
        try:
            # Verify the Firebase ID token
            decoded_token = self.verify_token_from_request(request)
            if not decoded_token:
                return Response("Invalid or expired token", status=status.HTTP_401_UNAUTHORIZED)

            # Extract the user ID from the decoded token
            user_id = decoded_token.get('user_id')

            # Check if a review from the user already exists
            existing_review = Review.objects.filter(user_id=user_id).first()

            if existing_review:
                # If a review already exists for the user, return a response indicating it's not a unique user
                return Response("notunique", status=status.HTTP_400_BAD_REQUEST)

            # If a review doesn't exist, proceed with creating a new review
            return super().create(request, *args, **kwargs)

        except Exception as e:
            # Handle any errors that occur during Firebase token verification
            return Response(str(e), status=status.HTTP_401_UNAUTHORIZED)

    def list(self, request, *args, **kwargs):
        try:
            # Verify the Firebase ID token
            decoded_token = self.verify_token_from_request(request)
            print(decoded_token)
            if not decoded_token:
                return Response("Invalid or expired token", status=status.HTTP_401_UNAUTHORIZED)

            # Proceed with the default get method if token is valid
            return super().list(request, *args, **kwargs)

        except Exception as e:
            # Handle any errors that occur during Firebase token verification
            return Response(str(e), status=status.HTTP_401_UNAUTHORIZED)
        
############ [ + ] token secured
class SalonReviews(FirebaseTokenVerificationMixin, APIView):
    def get_object(self, pk):
        print('ver1')
        try:
            return Salon.objects.get(pk=pk)
        except Salon.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        # Pobierz token z nagłówka 'Authorization'
        print('ver1')
        authorization_header = request.headers.get('Authorization')
        print('ver2')
        # Sprawdź czy nagłówek istnieje i czy zawiera token
        if authorization_header and authorization_header.startswith('Bearer '):
            # Podziel nagłówek i pobierz sam token
            token = authorization_header.split(' ')[1]

            # Weryfikuj token Firebase
            decoded_token = self.verify_firebase_token(token)
            if not decoded_token:
                return Response({'error': 'Invalid or expired token'}, status=status.HTTP_401_UNAUTHORIZED)
            print('ver3')
            # Token zweryfikowany, kontynuuj
            salon = self.get_object(pk)
            reviews = Review.objects.filter(salon=salon)
            serializer = ReviewSerializer(reviews, many=True)
            return Response(serializer.data)
        else:
            print('ver4')
            # Jeśli nagłówek 'Authorization' nie istnieje lub nie zawiera tokenu, zwróć błąd
            return Response({'error': 'Unauthorized. Token missing or invalid'}, status=status.HTTP_401_UNAUTHORIZED)

############ [ + ] token secured
class FixedOperatingHoursViewSet(FirebaseTokenVerificationMixin, viewsets.ModelViewSet):
    queryset = FixedOperatingHours.objects.all()
    serializer_class = FixedOperatingHoursSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['salon']  # Add this line to specify the filtering field

    def verify_token_from_request(self, request):
        authorization_header = request.headers.get('Authorization')
        if authorization_header and authorization_header.startswith('Bearer '):
            token = authorization_header.split(' ')[1]
            decoded_token = self.verify_firebase_token(token)
            return decoded_token
        return None
    
    def list(self, request, *args, **kwargs):
        try:
            # Verify the Firebase ID token
            decoded_token = self.verify_token_from_request(request)
            # if not decoded_token:
            #     return Response("Invalid or expired token", status=status.HTTP_401_UNAUTHORIZED)
                
            return super(FixedOperatingHoursViewSet, self).list(request, *args, **kwargs)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def create(self, request, *args, **kwargs):
        try:
            # Verify the Firebase ID token
            # decoded_token = self.verify_token_from_request(request)
            # if not decoded_token:
            #     return Response("Invalid or expired token", status=status.HTTP_401_UNAUTHORIZED)

            if isinstance(request.data, list):  # Check if the request is a list.
                 # Extract salon_id from request data
                salon_id = request.data[0]['salon']
                print('salon_id: ')
                print(salon_id)

                # Delete existing records for the given salon_id
                FixedOperatingHours.objects.filter(salon=salon_id).delete()
                print('Fixedop deleted')
                GeneratedTimeSlots.objects.filter(salon=salon_id).delete()
                print('Fixedop deleted')
                serializer = self.get_serializer(data=request.data, many=True)
                if serializer.is_valid():
                    serializer.save()
                    print('object saved')
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            else:
                return super(FixedOperatingHoursViewSet, self).create(request, *args, **kwargs)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

############ [ + ] token secured
class UnFixedOperatingHoursViewSet(FirebaseTokenVerificationMixin, viewsets.ModelViewSet):
    queryset = UnFixedOperatingHours.objects.all()
    serializer_class = UnFixedOperatingHoursSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['salon']  # Add this line to specify the filtering field

    def verify_token_from_request(self, request):
        authorization_header = request.headers.get('Authorization')
        if authorization_header and authorization_header.startswith('Bearer '):
            token = authorization_header.split(' ')[1]
            decoded_token = self.verify_firebase_token(token)
            return decoded_token
        return None

    def list(self, request, *args, **kwargs):
        try:
            # Verify the Firebase ID token
            decoded_token = self.verify_token_from_request(request)
            if not decoded_token:
                return Response("Invalid or expired token", status=status.HTTP_401_UNAUTHORIZED)

            return super().list(request, *args, **kwargs)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def create(self, request, *args, **kwargs):
        try:
            # Verify the Firebase ID token
            decoded_token = self.verify_token_from_request(request)
            if not decoded_token:
                return Response("Invalid or expired token", status=status.HTTP_401_UNAUTHORIZED)

            if isinstance(request.data, list):  # Check if the request is a list.
                serializer = self.get_serializer(data=request.data, many=True)
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            else:
                return super(UnFixedOperatingHoursViewSet, self).create(request, *args, **kwargs)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

############ [ + ] token secured
class GeneratedTimeSlotsViewSet(FirebaseTokenVerificationMixin, viewsets.ModelViewSet):
    queryset = GeneratedTimeSlots.objects.all().order_by('salon', 'date', 'time_from')
    serializer_class = GeneratedTimeSlotsSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['salon']
    ordering_fields = ['salon', 'date', 'time_from']

    def verify_token_from_request(self, request):
        authorization_header = request.headers.get('Authorization')
        if authorization_header and authorization_header.startswith('Bearer '):
            token = authorization_header.split(' ')[1]
            decoded_token = self.verify_firebase_token(token)
            return decoded_token
        return None

    def list(self, request, *args, **kwargs):
        try:
            # Verify the Firebase ID token
            decoded_token = self.verify_token_from_request(request)
            if not decoded_token:
                return Response("Invalid or expired token", status=status.HTTP_401_UNAUTHORIZED)

            return super().list(request, *args, **kwargs)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def retrieve(self, request, *args, **kwargs):
        try:
            # Verify the Firebase ID token
            decoded_token = self.verify_token_from_request(request)
            if not decoded_token:
                return Response("Invalid or expired token", status=status.HTTP_401_UNAUTHORIZED)

            return super().retrieve(request, *args, **kwargs)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def create(self, request, *args, **kwargs):
        try:
            # Verify the Firebase ID token
            decoded_token = self.verify_token_from_request(request)
            if not decoded_token:
                return Response("Invalid or expired token", status=status.HTTP_401_UNAUTHORIZED)

            return super().create(request, *args, **kwargs)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class AppointmentListView(APIView):
    def get(self, request, salon_id):
        try:
            # Pobierz wszystkie terminy wizyt dla danego salonu
            appointments = Appointment.objects.filter(salon_id=salon_id)
            # Serializuj dane
            serializer = AppointmentReadSerializer(appointments, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


############ [ + ] token secured

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags


class AppointmentViewSet(FirebaseTokenVerificationMixin, viewsets.ModelViewSet):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentWriteSerializer

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return AppointmentReadSerializer
        return AppointmentWriteSerializer

    def verify_token_from_request(self, request):
        authorization_header = request.headers.get('Authorization')
        if authorization_header and authorization_header.startswith('Bearer '):
            token = authorization_header.split(' ')[1]
            decoded_token = self.verify_firebase_token(token)
            return decoded_token
        return None
    
    def list(self, request, *args, **kwargs):
        try:
            # Verify the Firebase ID token
            decoded_token = self.verify_token_from_request(request)
            if not decoded_token:
                return Response("Invalid or expired token", status=status.HTTP_401_UNAUTHORIZED)

            # Call the original list method to retrieve the list of appointments
            return super().list(request, *args, **kwargs)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def create(self, request, *args, **kwargs):
        try:
            # Verify the Firebase ID token
            decoded_token = self.verify_token_from_request(request)
            if not decoded_token:
                return Response("Invalid or expired token", status=status.HTTP_401_UNAUTHORIZED)

            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['put'])
    def update_status(self, request, pk=None):
        try:
            print(request)
            # Verify the Firebase ID token
            decoded_token = self.verify_token_from_request(request)
            if not decoded_token:
                print('eh')
                return Response("Invalid or expired token", status=status.HTTP_401_UNAUTHORIZED)

            appointment = self.get_object()
            new_status = request.query_params.get('status', None)

            if new_status is None:
                return Response({"message": "Status parameter missing in the URL"}, status=status.HTTP_400_BAD_REQUEST)

            # Check if the status is not one of the expected values or not uppercase
            valid_statuses = {'X', 'F', 'C', 'P'}
            if new_status.upper() not in valid_statuses:
                return Response({"message": "Invalid status code"}, status=status.HTTP_400_BAD_REQUEST)

            appointment.status = str(new_status)
            appointment.save()

            services = list(appointment.services.all())

            # Send email based on status change
            if new_status.upper() == 'C':  # Example: 'C' for Confirmed
                self.send_status_confirmation_update_email(appointment.customer, appointment, appointment.salon.id, services)

            elif new_status.upper() == 'X':  # Example: 'X' for Canceled
                self.send_status_canceled_update_email(appointment.customer, appointment, appointment.salon.id, services)

            return Response({"message": f"Status updated to '{new_status}' successfully"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def send_status_confirmation_update_email(self, customer, appointment, salon_id, services):
        try:
            firebase_user = FirebaseUsers.objects.get(firebase_uid=customer)
            salon = Salon.objects.get(id=salon_id)
            print('try')
            # Prepare email content
            date = appointment.date_of_booking.strftime('%Y-%m-%d')
            subject = f'Wizyta potwierdzona - [{date}]'
            from_email = f'Findovio | Rezerwacja {salon.name} <rezerwacje@findovio.nl>'
            to_email = firebase_user.firebase_email
            to_email_biz = salon.email
            bcc_email = ['damian@findovio.nl']
            salon_address = f"{salon.address_street} {salon.address_number}, {salon.address_postal_code} {salon.address_city}"
            salon_google_address = f"https://www.google.com/maps/place/{salon.address_city}, {salon.address_postal_code}, {salon.address_street} {salon.address_number}"

            total_duration_minutes = sum(service.duration_minutes for service in services)
            print('try1')
            html_content = render_to_string('appointment_confirmed_template_client.html', {
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
            print('try2')
            html_content_to_biz = render_to_string('appointment_confirmed_template_biz.html', {
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
                print('try3')
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

        except Exception as e:
                print(f"Error sending email: {e}")

    def send_status_canceled_update_email(self, customer, appointment, salon_id, services):
        firebase_user = FirebaseUsers.objects.get(firebase_uid=customer)
        salon = Salon.objects.get(id=salon_id)
        print('try4')
        # Prepare email content
        date = appointment.date_of_booking.strftime('%Y-%m-%d')
        subject = f'Anulowanie wizyty - [{date}]'
        from_email = f'Findovio | Rezerwacja {salon.name} <rezerwacje@findovio.nl>'
        to_email = firebase_user.firebase_email
        to_email_biz = salon.email
        bcc_email = ['damian@findovio.nl']
        salon_address = f"{salon.address_street} {salon.address_number}, {salon.address_postal_code} {salon.address_city}"
        salon_google_address = f"https://www.google.com/maps/place/{salon.address_city}, {salon.address_postal_code}, {salon.address_street} {salon.address_number}"

        total_duration_minutes = sum(service.duration_minutes for service in services)
        
        html_content = render_to_string('appointment_canceled_template_client.html', {
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

        html_content_to_biz = render_to_string('appointment_canceled_template_biz.html', {
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
            print('try4')
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

    def delete(self, request, *args, **kwargs):
        try:
            # Verify the Firebase ID token
            decoded_token = self.verify_token_from_request(request)
            if not decoded_token:
                return Response("Invalid or expired token", status=status.HTTP_401_UNAUTHORIZED)

            appointment = self.get_object()

            # Set the is_available field of each timeslot back to True
            for timeslot in appointment.timeslots.all():
                timeslot.is_available = True
                timeslot.save()

            # Delete the appointment
            appointment.delete()

            # Return a custom success response
            return Response({"message": "Appointment deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

############ [ + ] token secured
class UserAppointmentsListView(FirebaseTokenVerificationMixin, ListAPIView):
    serializer_class = AppointmentReadSerializer # Allow any user to access this view

    def verify_token_from_request(self, request):
        authorization_header = request.headers.get('Authorization')
        if authorization_header and authorization_header.startswith('Bearer '):
            token = authorization_header.split(' ')[1]
            decoded_token = self.verify_firebase_token(token)
            return decoded_token
        return None

    def get_queryset(self):
        decoded_token = self.verify_token_from_request(self.request)
        if not decoded_token:
            # If token verification fails, return an empty queryset
            return Appointment.objects.none()
        # Get the user ID from the decoded token
        user_id = self.request.query_params.get('user_id')
        if user_id is not None:
            return Appointment.objects.filter(customer=user_id)
        return Appointment.objects.none()


    # def get_queryset(self, request):
    #     user_id = self.request.query_params.get('user_id')
    #     if user_id is not None:
    #         return Appointment.objects.filter(customer=user_id)
    #     return Appointment.objects.none()
    # def list(self, request, *args, **kwargs):
    #     try:
    #         # Verify the Firebase ID token
    #         decoded_token = self.verify_token_from_request(request)
    #         if not decoded_token:
    #             return Response("Invalid or expired token", status=status.HTTP_401_UNAUTHORIZED)

    #         # Call the original list method to retrieve the list of appointments
    #         return super().list(request, *args, **kwargs)
    #     except Exception as e:
    #         return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # def create(self, request, *args, **kwargs):
    #     try:
    #         # Verify the Firebase ID token
    #         decoded_token = self.verify_token_from_request(request)
    #         if not decoded_token:
    #             return Response("Invalid or expired token", status=status.HTTP_401_UNAUTHORIZED)

    #         serializer = AppointmentWriteSerializer(data=request.data)
    #         serializer.is_valid(raise_exception=True)
    #         self.perform_create(serializer)
    #         headers = self.get_success_headers(serializer.data)
    #         return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    #     except Exception as e:
    #         return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # def delete(self, request, *args, **kwargs):
    #     try:
    #         # Verify the Firebase ID token
    #         decoded_token = self.verify_token_from_request(request)
    #         if not decoded_token:
    #             return Response("Invalid or expired token", status=status.HTTP_401_UNAUTHORIZED)

    #         # Call the original delete method to delete the appointment
    #         return super().delete(request, *args, **kwargs)
    #     except Exception as e:
    #         return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

############ [ - ] not secured
class KeywordsCounterViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = KeywordsCounter.objects.all().order_by('-count')[:20]
    serializer_class = KeywordsCounterSerializer

# Your view function
def getTopCities(request):
    city_counts = (
        Salon.objects
        .annotate(lower_city=Lower('address_city'))  # Convert city names to lowercase
        .values('lower_city')
        .annotate(city_count=Count('lower_city'))
        .annotate(city=F('lower_city'))  # Rename the city back to its original case
        .order_by('-city_count')[:20]
    )
    
    top_cities = [{'word': city['city'], 'count': city['city_count']} for city in city_counts]
    
    return JsonResponse(top_cities, safe=False)

############ [ - ] not secured
class AvatarBySalonNameView(APIView):
    serializer_class = AvatarBySalonNameSerializer

    def get(self, request, *args, **kwargs):
        salon_name = request.query_params.get('salon_name')
        print(request.query_params.get('salon_name'))

        if salon_name:
            formatted_salon_name = quote(salon_name)
            serializer = self.serializer_class(context={'salon_name': formatted_salon_name})
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Salon name not provided"}, status=status.HTTP_400_BAD_REQUEST)

############ [ - ] not secured        
class AdvertisementListCreateView(generics.ListCreateAPIView):
    queryset = Advertisement.objects.all()
    serializer_class = AdvertisementSerializer

    def perform_create(self, serializer):
        # Dodawanie informacji o zalogowanym użytkowniku do reklamy
        serializer.save()

# EXAMPLE
#{
#    "id": 1,
#    "banner_style": 1,
#    "promotion_level": 1,
#    "salon": 16,
#    "Title_line_1": "Rabat 25%",
#    "Title_line_2": "Salon Jeden",
#    "Text_line_1": "Wielka promocja",
#    "Text_line_2": "",
#    "Special_text": "Tylko dziś!",
#    "Date_of_order": "2023-11-20T21:33:04.441947Z",
#    "Date_start": "2023-11-20",
#    "Date_end": "2023-11-27",
#    "promotion_price": 120.0,
#    "image": "http://185.180.204.182/reklama.webp"
#}

############ [ - ] not secured
class AdvertisementListView(APIView):

    def get(self, request):
        advertisements = Advertisement.objects.all()
        serializer = AdvertisementSerializer(advertisements, many=True)
        return Response(serializer.data)

############ [ - ] not secured
class FindovioAdvertisementListCreateView(generics.ListCreateAPIView):
    queryset = FindovioAdvertisement.objects.all()
    serializer_class = FindovioAdvertisementSerializer

############ [ - ] not secured
class FindovioAdvertisementDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = FindovioAdvertisement.objects.all()
    serializer_class = FindovioAdvertisementSerializer

############ [ - ] not secured
class CheckNameExists(APIView):
    def post(self, request, *args, **kwargs):
        name = request.data.get('name', None)
        print("Received name:", name)
        if not name:
            return Response({'error': 'Name parameter is required'}, status=400)

        salon_exists = Salon.objects.filter(name=name).exists()
        if salon_exists:
            return Response({'exists': True}, status=200)
        else:
            return Response({'exists': False}, status=200)
        
class SalonImageViewFinal(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request, *args, **kwargs):
        # Pobieramy plik bezpośrednio z request.FILES
        file = request.FILES.get('file')
        json_data = json.loads(request.POST.get('jsonData'))
        photo_type = json_data.get('photoType')
        salon_id = json_data.get('salon_id')
        print('Data correct')

        # Ensure photo_type is valid
        if photo_type not in ['avatar', 'gallery']:
            print('Invalid phototype')
            return Response({'error': 'Invalid photoType'}, status=status.HTTP_400_BAD_REQUEST)
        print('Phototype correct')

        try:
            # Konwertujemy obraz do formatu WebP
            try:
                image = Image.open(file)
                filename = f'{salon_id}_{photo_type}.webp'  # Tworzymy nazwę pliku na podstawie salon_id i photo_type
                webp_buffer = BytesIO()
                image.save(webp_buffer, format='WEBP')
                webp_content = ContentFile(webp_buffer.getvalue(), name=filename)
            except Exception as e:
                print(f'Error converting a file: {e}')
                return Response({'error': 'Error converting a file'}, status=status.HTTP_400_BAD_REQUEST)
            print('Convert correct')

            # Save SalonImage instance
            try:
                salon_image_data = {'salon_id': salon_id, 'image': webp_content, 'image_type': photo_type}
                serializer = SalonImageSerializerFinal(data=salon_image_data, context={'request': request})
                serializer.is_valid(raise_exception=True)  # Rzuca wyjątek, jeśli dane nie są poprawne
            except Exception as e:
                print(f'Error serializing a file: {e}')
                return Response({'error': 'Error serializing a file'}, status=status.HTTP_400_BAD_REQUEST)
            print('Serializer correct')
            
            serializer.save()

             # Pobieramy adres URL zapisanej instancji SalonImageFinal
            image_url = serializer.instance.image.url

            # Aktualizujemy pole 'avatar' w modelu Salon na adres URL
            salon = Salon.objects.get(id=salon_id)
            if photo_type == 'avatar':
                salon.avatar = f'http://185.180.204.182{image_url}'
            elif photo_type == 'gallery':
                if not salon.gallery:
                    salon.gallery = [f'http://185.180.204.182{image_url}']
                else:
                    salon.gallery.append(f'http://185.180.204.182{image_url}')
            salon.save()
            print('Save correct')
            return Response({'message': 'File uploaded and converted to WebP successfully'}, status=status.HTTP_201_CREATED)
        except Exception as e:
            print(f'Error saving file: {e}')
            return Response({'error': 'Failed to save the file'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    def get(self, request, *args, **kwargs):
        print('1')
        photo_type = kwargs.get('photo_type')
        print('2')
        salon_id = kwargs.get('salon_id')
        # Ensure photo_type is valid
        try:
            if photo_type not in ['avatar', 'gallery']:
                print('2a')
                return Response({'error': 'wrong phototype'}, status=status.HTTP_400_BAD_REQUEST)
        except SalonImage.DoesNotExist:
            print('2b')
            return Response({'error': 'Images not found'}, status=status.HTTP_404_NOT_FOUND)
        

        try:
            print('3')
            salon_images = SalonImageFinal.objects.filter(salon_id=salon_id, image_type=photo_type)
            print('4')
            serializer = SalonImageSerializerFinal(salon_images, context={"request": request}, many=True)
            print('6')
            return Response(serializer.data)
        except SalonImage.DoesNotExist:
            return Response({'error': 'Images not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            print('Zesralo sie tu: ')
            print(e)
            return Response({'error' : 'Error serializer'}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk):
        try:
            salon_image = SalonImageFinal.objects.get(pk=pk)
            salon_image.delete()
            return Response({'message': 'Image deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
        except SalonImageFinal.DoesNotExist:
            raise NotFound("Image not found")
        except Exception as e:
            print(f'Error deleting image: {e}')
            return Response({'error': 'Failed to delete image'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class DeleteSalonImageView(viewsets.ViewSet):
    def destroy(self, request, pk):
        try:
            salon_image = SalonImageFinal.objects.get(pk=pk)
            print('1')
            salon_image.delete()
            print('2')
            return Response({'message': 'Image deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
        except SalonImageFinal.DoesNotExist:
            print('Error deleting image:')
            raise NotFound("Image not found")
        except Exception as e:
            print(f'Error deleting image: {e}')
            return Response({'error': 'Failed to delete image'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def check_salon(request, salon_id):
    try:
        salon = Salon.objects.get(id=salon_id)
        services = Service.objects.filter(salon=salon)
        categories = Category.objects.filter(salon=salon)
        avatar_image = SalonImageFinal.objects.filter(salon_id=salon_id, image_type='avatar').first()

        missing_data = []

        if not salon:
            return HttpResponseNotFound('Salon does not exist.')

        if not services.exists():
            missing_data.append('services')
        elif services.filter(category__isnull=True).exists():
            missing_data.append('service category')

        if not categories.exists():
            missing_data.append('categories')

        if not avatar_image:
            missing_data.append('avatar image')

        if missing_data:
            return JsonResponse({'message': f'Some data is missing or invalid for the salon: {", ".join(missing_data)}.', 'status': 'error'}, status=500)
        else:
            return JsonResponse({'message': 'Salon is correctly created.', 'status': 'success'}, status=201)
            
    except Exception as e:
        return HttpResponseServerError(str(e))


class LicenseCreateView(APIView):
    def post(self, request):
        username = request.data.get('username')
        if License.objects.filter(username=username).exists():
            return Response({"error": "Username already exists."}, status=status.HTTP_400_BAD_REQUEST)
        license = License.objects.create(username=username)
        serializer = LicenseSerializer(license)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class LicenseDetailView(APIView):
    def get_object(self, username):
        try:
            return License.objects.get(username=username)
        except License.DoesNotExist:
            raise Http404

    def get(self, request, username):
        license = self.get_object(username)
        serializer = LicenseSerializer(license)
        return Response(serializer.data)

    def put(self, request, username):
        license = self.get_object(username)
        serializer = LicenseSerializer(license, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, username):
        license = self.get_object(username)
        license.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class AddPaymentView(APIView):
    def post(self, request):
        serializer = PaymentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

from django.utils.timezone import now
class LicenseStatusView(APIView):

    def get(self, request, username):
        try:
            license_instance = License.objects.get(username=username)
        except License.DoesNotExist:
            return Response({'error': 'License not found'}, status=status.HTTP_404_NOT_FOUND)

        try:
            # Get the creation date and current date
            creation_date = license_instance.created_at
            current_date = now()

            # Calculate days since creation
            days_since_creation = (current_date - creation_date).days

            if license_instance.kind_of_license == 0:  # Free license
                remaining_days = 30 - days_since_creation
                is_active = remaining_days >= 0
            else:
                last_payment = license_instance.payments.latest('date')
                days_since_last_payment = (current_date - last_payment.date).days
                if license_instance.kind_of_license == 0 and len(license_instance.payments.all()) > 1 and days_since_last_payment > 45:
                    remaining_days = days_since_last_payment - 30
                    is_active = False
                else:
                    remaining_days = 30 - days_since_last_payment
                    is_active = remaining_days >= 0

            return Response({
                'remaining_days': remaining_days,
                'is_active': is_active
            })

        except Exception as e:
            print(f"An error occurred: {e}")
            return Response({'error': f"An error occurred: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

from django.db.models import Q

class SearchView(APIView):
    def get(self, request, *args, **kwargs):
        query = request.GET.get('q', '').lower()

        # Przeszukiwanie salonów
        salons = Salon.objects.filter(
            Q(name__icontains=query) |
            Q(address_city__icontains=query) |
            Q(address_street__icontains=query) |
            Q(address_postal_code__icontains=query)
        )

        # Przeszukiwanie usług
        services = Service.objects.filter(
            Q(title__icontains=query) 
        )

        # Przeszukiwanie kategorii
        categories = Category.objects.filter(
            Q(name__icontains=query) 
        )

        salon_serializer = SalonSearchSerializer(salons, many=True)
        service_serializer = ServiceSearchSerializer(services, many=True)
        category_serializer = CategorySearchSerializer(categories, many=True)

        # Usuwanie powtórzeń
        unique_services_and_categories = {item['title']: item for item in service_serializer.data}
        unique_services_and_categories.update({item['name']: item for item in category_serializer.data})
        unique_services_and_categories_list = list(unique_services_and_categories.values())

        results = {
            'services': unique_services_and_categories_list,
            'places': salon_serializer.data,
        }

        return Response(results)
