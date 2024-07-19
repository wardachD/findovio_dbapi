from django.contrib.postgres.search import TrigramSimilarity
from django.db import connection
from django.db.models.query import Prefetch
from geopy.geocoders import Nominatim
from django.contrib.gis.geos import Point
from django.db.models import TextField, Q
from django.db.models.functions import Cast
from .models import Salon, Category, Service, KeywordsCounter

## -------------------------------------------------------> 
## By Keywords, address and radius
from django.db.models import Q, TextField
from django.contrib.postgres.search import TrigramSimilarity
from django.db.models.functions import Cast

from django.db.models import Q, F, TextField
from django.contrib.postgres.search import TrigramSimilarity
from django.db.models.functions import Cast

from django.http import JsonResponse

def search_salons(keywords, address, category=None):
    try:
        print("search salon [1]")
        radius = 2000
        salons = Salon.objects.none()

        # Jeśli tylko miasto i promień są podane
        if address and not keywords:
            print("if address and not keywords:")
            point = get_point_from_address(address)
            cursor = connection.cursor()
            print("if address and not keywords:")
            cursor.execute(
                '''
                SELECT id, location, ST_Distance(
                    location,
                    ST_SetSRID(ST_MakePoint(%s, %s)::geography, 4326)
                ) AS distance
                FROM findoviodb_salon
                WHERE ST_Distance(
                    location,
                    ST_SetSRID(ST_MakePoint(%s, %s)::geography, 4326)
                ) <= %s
                ''',
                [point.x, point.y, point.x, point.y, radius]
            )
            print("if address and not keywords:")
            salon_ids = [row[0] for row in cursor.fetchall()]
            print("if address and not keywords1:")
            salons_by_radius = Salon.objects.filter(id__in=salon_ids)
            print("count:")
            print(salons_by_radius.count)
            salons_by_address = Salon.objects.annotate(
                similarity_address_city=TrigramSimilarity('address_city', address),
                similarity_address_street=TrigramSimilarity('address_street', address)
            ).filter(
                Q(similarity_address_city__gte=0.1) |
                Q(similarity_address_street__gte=0.1)
            ).distinct()
            print("if address and not keywords3:")
            try:
                salons = salons_by_address.union(salons)
            except Exception as e:
                print(e)
            print("if address and not keywords4:")

        # Jeśli tylko słowo kluczowe jest podane
        elif keywords and not address:
            print("elif keywords and not address:")
            update_keywords(keywords)
            salons = Salon.objects.annotate(
                similarity_name=TrigramSimilarity('name', keywords),
                similarity_address_city=TrigramSimilarity('address_city', keywords),
                similarity_address_street=TrigramSimilarity('address_street', keywords),
                similarity_about=TrigramSimilarity('about', keywords),
                similarity_categories=TrigramSimilarity(Cast('categories__name', TextField()), keywords),
                similarity_services=TrigramSimilarity(Cast('categories__services__title', TextField()), keywords)
            ).filter(
                Q(similarity_name__gte=0.35) |
                Q(similarity_address_city__gte=0.35) |
                Q(similarity_address_street__gte=0.35) |
                Q(similarity_about__gte=0.35) |
                Q(similarity_categories__gte=0.35) |
                Q(similarity_services__gte=0.35)
            ).distinct().annotate(
                max_similarity=F('similarity_name') + F('similarity_address_city') + F('similarity_address_street') +
                               F('similarity_about') + F('similarity_categories') + F('similarity_services')
            ).order_by('-max_similarity')
            for salon in salons:
                print(f"Salon: {salon.name}, Similarity: {salon.max_similarity}, "
                      f"Name: {salon.similarity_name}, City: {salon.similarity_address_city}, "
                      f"Street: {salon.similarity_address_street}, About: {salon.similarity_about}, "
                      f"Categories: {salon.similarity_categories}, Services: {salon.similarity_services}")
            print("elif keywords and not address:")

        # Jeśli zarówno adres, jak i słowo kluczowe są podane
        elif address and keywords:
            print("elif address and keywords:")
            point = get_point_from_address(address)
            cursor = connection.cursor()
            print("elif address and keywords:")
            cursor.execute(
                '''
                SELECT id, location, ST_Distance(
                    location,
                    ST_SetSRID(ST_MakePoint(%s, %s)::geography, 4326)
                ) AS distance
                FROM findoviodb_salon
                WHERE ST_Distance(
                    location,
                    ST_SetSRID(ST_MakePoint(%s, %s)::geography, 4326)
                ) <= %s
                ''',
                [point.x, point.y, point.x, point.y, radius]
            )
            print("elif address and keywords:")
            salon_ids = [row[0] for row in cursor.fetchall()]
            salons_by_radius = Salon.objects.filter(id__in=salon_ids).distinct()
            print("count:")
            print(salons_by_radius.count)
            salons_by_address = Salon.objects.annotate(
                similarity_address_city=TrigramSimilarity('address_city', address),
                similarity_address_street=TrigramSimilarity('address_street', address)
            ).filter(
                Q(similarity_address_city__gte=0.1) |
                Q(similarity_address_street__gte=0.1)
            ).distinct()
            combined_salons = salons_by_radius | salons_by_address
            print("elif address and keywords:")
            
            update_keywords(keywords)
            salons = combined_salons.annotate(
                similarity_name=TrigramSimilarity('name', keywords),
                similarity_address_city=TrigramSimilarity('address_city', keywords),
                similarity_address_street=TrigramSimilarity('address_street', keywords),
                similarity_about=TrigramSimilarity('about', keywords),
                similarity_categories=TrigramSimilarity(Cast('categories__name', TextField()), keywords),
                similarity_services=TrigramSimilarity(Cast('categories__services__title', TextField()), keywords)
            ).filter(
                Q(similarity_name__gte=0.35) |
                Q(similarity_address_city__gte=0.35) |
                Q(similarity_address_street__gte=0.35) |
                Q(similarity_about__gte=0.35) |
                Q(similarity_categories__gte=0.35) |
                Q(similarity_services__gte=0.35)
            ).distinct()
            print("elif address and keywords:")

        # Filtracja według kategorii, jeśli jest podana
        # if category:
        #     salons = salons.filter(flutter_category=category)
        #     print('filtered search_salons(keywords, address, radius, category=None):')

        result = set(salons)
        print(result)

        print("search salon [4]")
        return result

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)




# Reszta funkcji pozostaje bez zmian


## By Keywords, address and radius
## -------------------------------------------------------> 


## By Keywords
def search_by_keywords(keywords, category=None):

    if keywords == '':
        salons_results = Salon.objects.all()
    else:
        update_keywords(keywords)
        salons = Salon.objects.annotate(
            similarity_name=TrigramSimilarity('name', keywords),
            similarity_address_city=TrigramSimilarity('address_city', keywords),
            similarity_about=TrigramSimilarity('about', keywords),
            similarity_categories=TrigramSimilarity(Cast('categories', TextField()), keywords),
            similarity_salon_categories=TrigramSimilarity(Cast('salon_categories', TextField()), keywords)
        ).filter(
            Q(similarity_name__gte=0.35) |
            Q(similarity_address_city__gte=0.35) |
            Q(similarity_about__gte=0.35) |
            Q(similarity_categories__gte=0.35) |
            Q(similarity_salon_categories__gte=0.35)
        ).distinct()  # Dodajemy metodę distinct()

    salon_results = salons.filter(id__in=salons).distinct()

    # if category:
    #     salon_results = salons.filter(flutter_category=category)
    #     print('filtered search_by_keywords(keywords, category=None):')
    
    # Pobieranie powiązanych kategorii i usług dla wyników z modelu Salon
    salon_results = salon_results.prefetch_related(
        Prefetch('categories', queryset=Category.objects.all()),
        Prefetch('salon_categories', queryset=Service.objects.all())
    )

    return salon_results


## By Keywords
## -------------------------------------------------------> 

## -------------------------------------------------------> 

## By Address

def search_by_address_radius(address, radius, category=None):
    if address:
        salonsTemp = Salon.objects.all()
        #salons = salonsTemp.filter(address_city__icontains=address)
        point = get_point_from_address(address)
        # Tworzenie zapytania SQL z użyciem kursora
        cursor = connection.cursor()
        cursor.execute(
                '''
                SELECT id, location, ST_Distance(
                    location,
                    ST_SetSRID(ST_MakePoint(%s, %s)::geography, 4326)
                ) AS distance
                FROM findoviodb_salon
                WHERE ST_DWithin(
                    location,
                    ST_SetSRID(ST_MakePoint(%s, %s)::geography, 4326),
                    %s
                )
                ''',
                [point.x, point.y, point.x, point.y, radius]
        )
        salon_ids = []
        salon_distances = {}
        for row in cursor.fetchall():
            salon_id = row[0]
            salon_ids.append(salon_id)
            distance_m = row[2]
            salon_distances[salon_id] = distance_m  # Convert back to meters

        salons = Salon.objects.filter(id__in=salon_ids)
        print("search salon [3]")
        # Aktualizacja pola distance_from_query dla każdego salonu
        for salon in salons:
            salon.distance_from_query = salon_distances[salon.id]
            salon.save()  # Zapis wartości do modelu

    # if category:
    #     salons = salons.filter(flutter_category=category)
    #     print('filtered search_by_address_radius(address, radius, category=None):')

    return salons


## -------------------------------------------------------> 

## -------------------------------------------------------> 
## Get point from address

def get_point_from_address(address):
    geolocator = Nominatim(user_agent='findovio')
    location = geolocator.geocode(address)
    if location:
        point = Point(float(location.latitude), float(location.longitude), srid=4326)
        print(point)
        return point
    return None

## -------------------------------------------------------> 

## -------------------------------------------------------> 
## Count keywords
## This is used as a list of keywords in a keyword search fields
## New words are added with counter equal to 1
## Existing words just adds a 1 to counter

def update_keywords(keywords):
    keyword_list = keywords.split()
    for keyword in keyword_list:
        try:
            keyword_object = KeywordsCounter.objects.get(word=keyword)
            keyword_object.count += 1
            keyword_object.save()
        except KeywordsCounter.DoesNotExist:
            KeywordsCounter.objects.create(word=keyword, count=1)

