from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
#from .serializers import CategorySerializer, ServiceSerializer, SalonSerializer
# from .models import Salon, Service, Category
"""
@api_view(['POST'])
def add_salon(request):
    serializer = SalonSerializer(data=request.data)
    if serializer.is_valid():
        salon = serializer.save()
        return Response({'status': 'success', 'id': salon.id}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def create_category(request):
    serializer = CategorySerializer(data=request.data)
    if serializer.is_valid():
        category = serializer.save()
        return Response({'status': 'success', 'id': category.id}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def create_service(request):
    serializer = ServiceSerializer(data=request.data)
    if serializer.is_valid():
        service = serializer.save()
        return Response({'status': 'success', 'id': service.id}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@csrf_exempt
def add_salon(request):
    if request.method == 'POST':
        name = request.POST.get('name', '')
        address_city = request.POST.get('address_city', '')
        address_postal_code = request.POST.get('address_postal_code', '')
        address_street = request.POST.get('address_street', '')
        address_number = request.POST.get('address_number', '')
        about = request.POST.get('about', '')
        phone_number = request.POST.get('phone_number', '')

        salon = Salon(
            name=name,
            address_city=address_city,
            address_postal_code=address_postal_code,
            address_street=address_street,
            address_number=address_number,
            about=about,
            phone_number=phone_number
        )
        salon.save()

        return JsonResponse({'status': 'success', 'id': salon.pk})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})


@csrf_exempt
def update_salon(request, salon_id):
    try:
        salon = Salon.objects.get(pk=salon_id)
    except Salon.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Salon not found'})

    if request.method == 'POST':
        name = request.POST.get('name', '')
        address_city = request.POST.get('address_city', '')
        address_postal_code = request.POST.get('address_postal_code', '')
        address_street = request.POST.get('address_street', '')
        address_number = request.POST.get('address_number', '')
        about = request.POST.get('about', '')
        phone_number = request.POST.get('phone_number', '')

        salon.name = name
        salon.address_city = address_city
        salon.address_postal_code = address_postal_code
        salon.address_street = address_street
        salon.address_number = address_number
        salon.about = about
        salon.phone_number = phone_number
        salon.save()

        return JsonResponse({'status': 'success'})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})


@csrf_exempt
def update_salon_field(request, salon_id):
    try:
        salon = Salon.objects.get(pk=salon_id)
    except Salon.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Salon not found'})

    if request.method == 'POST':
        field = request.POST.get('field', '')
        value = request.POST.get('value', '')

        if field == 'name':
            salon.name = value
        elif field == 'address_city':
            salon.address_city = value
        elif field == 'address_postal_code':
            salon.address_postal_code = value
        elif field == 'address_street':
            salon.address_street = value
        elif field == 'address_number':
            salon.address_number = value
        elif field == 'about':
            salon.about = value
        elif field == 'phone_number':
            salon.phone_number = value

        salon.save()

        return JsonResponse({'status': 'success'})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})


@csrf_exempt
def delete_salon(request, salon_id):
    try:
        salon = Salon.objects.get(pk=salon_id)
        salon.delete()
        return JsonResponse({'status': 'success'})
    except Salon.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Salon not found'})

@api_view(['POST'])
def create_category_with_services(request, salon_id):
    try:
        salon = Salon.objects.get(id=salon_id)
    except Salon.DoesNotExist:
        return Response({'error': 'Salon not found'}, status=status.HTTP_404_NOT_FOUND)

    serializer = CategorySerializer(data=request.data, context={'salon_id': salon_id})
    if serializer.is_valid():
        category_name = serializer.validated_data['name']
        list_services = serializer.validated_data['list_services']

        # Sprawdź, czy kategoria już istnieje dla danego salonu
        category_exists = Category.objects.filter(name=category_name, salon=salon).exists()

        if category_exists:
            # Kategoria już istnieje, dodaj tylko nowe usługi
            category = Category.objects.get(name=category_name, salon=salon)
            for service_data in list_services:
                Service.objects.create(category=category, **service_data)
        else:
            # Kategoria nie istnieje, utwórz nową kategorię wraz z usługami
            category = Category.objects.create(name=category_name)
            category.salon.add(salon)
            for service_data in list_services:
                Service.objects.create(category=category, **service_data)

        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) """
