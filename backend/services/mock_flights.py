import math
import random
from datetime import datetime, timedelta
from functools import lru_cache

AIRLINES = [
    {'name': 'Air Peace', 'code': 'P4', 'region': 'africa', 'trust_score': 4.1},
    {'name': 'Ethiopian Airlines', 'code': 'ET', 'region': 'africa', 'trust_score': 4.7},
    {'name': 'Kenya Airways', 'code': 'KQ', 'region': 'africa', 'trust_score': 4.3},
    {'name': 'RwandAir', 'code': 'WB', 'region': 'africa', 'trust_score': 4.5},
    {'name': 'Arik Air', 'code': 'W3', 'region': 'africa', 'trust_score': 3.8},
    {'name': 'IbomAir', 'code': 'Z9', 'region': 'africa', 'trust_score': 4.0},
    {'name': 'Emirates', 'code': 'EK', 'region': 'global', 'trust_score': 4.9},
    {'name': 'British Airways', 'code': 'BA', 'region': 'global', 'trust_score': 4.6},
    {'name': 'Turkish Airlines', 'code': 'TK', 'region': 'global', 'trust_score': 4.5},
    {'name': 'Qatar Airways', 'code': 'QR', 'region': 'global', 'trust_score': 4.8},
    {'name': 'Air France', 'code': 'AF', 'region': 'global', 'trust_score': 4.4},
    {'name': 'KLM', 'code': 'KL', 'region': 'global', 'trust_score': 4.5},
    {'name': 'Lufthansa', 'code': 'LH', 'region': 'global', 'trust_score': 4.6},
    {'name': 'South African Airways', 'code': 'SA', 'region': 'africa', 'trust_score': 4.2},
]

AIRPORTS = {
    'LOS': {'name': 'Murtala Muhammed International', 'city': 'Lagos', 'country': 'Nigeria', 'region': 'africa', 'lat': 6.5774, 'lon': 3.3210},
    'ABV': {'name': 'Nnamdi Azikiwe International', 'city': 'Abuja', 'country': 'Nigeria', 'region': 'africa', 'lat': 9.0064, 'lon': 7.2632},
    'PHC': {'name': 'Port Harcourt International', 'city': 'Port Harcourt', 'country': 'Nigeria', 'region': 'africa', 'lat': 5.0155, 'lon': 6.9496},
    'ACC': {'name': 'Kotoka International', 'city': 'Accra', 'country': 'Ghana', 'region': 'africa', 'lat': 5.6052, 'lon': -0.1668},
    'NBO': {'name': 'Jomo Kenyatta International', 'city': 'Nairobi', 'country': 'Kenya', 'region': 'africa', 'lat': -1.3192, 'lon': 36.9275},
    'ADD': {'name': 'Bole International', 'city': 'Addis Ababa', 'country': 'Ethiopia', 'region': 'africa', 'lat': 8.9779, 'lon': 38.7993},
    'JNB': {'name': 'O.R. Tambo International', 'city': 'Johannesburg', 'country': 'South Africa', 'region': 'africa', 'lat': -26.1367, 'lon': 28.2411},
    'CMN': {'name': 'Mohammed V International', 'city': 'Casablanca', 'country': 'Morocco', 'region': 'africa', 'lat': 33.3675, 'lon': -7.5898},
    'KGL': {'name': 'Kigali International', 'city': 'Kigali', 'country': 'Rwanda', 'region': 'africa', 'lat': -1.9686, 'lon': 30.1395},
    'DKR': {'name': 'Blaise Diagne International', 'city': 'Dakar', 'country': 'Senegal', 'region': 'africa', 'lat': 14.6736, 'lon': -17.4900},
    'DXB': {'name': 'Dubai International', 'city': 'Dubai', 'country': 'UAE', 'region': 'middle_east', 'lat': 25.2532, 'lon': 55.3657},
    'DOH': {'name': 'Hamad International', 'city': 'Doha', 'country': 'Qatar', 'region': 'middle_east', 'lat': 25.2609, 'lon': 51.6138},
    'LHR': {'name': 'Heathrow Airport', 'city': 'London', 'country': 'UK', 'region': 'europe', 'lat': 51.4700, 'lon': -0.4543},
    'CDG': {'name': 'Charles de Gaulle', 'city': 'Paris', 'country': 'France', 'region': 'europe', 'lat': 49.0097, 'lon': 2.5479},
    'AMS': {'name': 'Amsterdam Schiphol', 'city': 'Amsterdam', 'country': 'Netherlands', 'region': 'europe', 'lat': 52.3086, 'lon': 4.7639},
    'FRA': {'name': 'Frankfurt Airport', 'city': 'Frankfurt', 'country': 'Germany', 'region': 'europe', 'lat': 50.0379, 'lon': 8.5622},
    'IST': {'name': 'Istanbul Airport', 'city': 'Istanbul', 'country': 'Turkey', 'region': 'europe', 'lat': 41.2608, 'lon': 28.7419},
    'JFK': {'name': 'John F. Kennedy International', 'city': 'New York', 'country': 'USA', 'region': 'americas', 'lat': 40.6413, 'lon': -73.7781},
    'IAD': {'name': 'Dulles International', 'city': 'Washington DC', 'country': 'USA', 'region': 'americas', 'lat': 38.9531, 'lon': -77.4565},
    'YYZ': {'name': 'Toronto Pearson International', 'city': 'Toronto', 'country': 'Canada', 'region': 'americas', 'lat': 43.6777, 'lon': -79.6248},
}

BASE_PRICES = {
    # Domestic Nigeria
    ('LOS', 'ABV'): (80, 150),
    ('LOS', 'PHC'): (90, 180),
    ('ABV', 'PHC'): (70, 140),
    # West Africa
    ('LOS', 'ACC'): (200, 450),
    ('ABV', 'ACC'): (220, 480),
    # East/Southern Africa
    ('LOS', 'NBO'): (350, 700),
    ('LOS', 'ADD'): (380, 750),
    ('LOS', 'JNB'): (400, 800),
    ('NBO', 'ADD'): (150, 300),
    ('NBO', 'JNB'): (250, 500),
    # North Africa
    ('LOS', 'CMN'): (300, 600),
    # Middle East
    ('LOS', 'DXB'): (450, 900),
    ('LOS', 'DOH'): (470, 950),
    ('ABV', 'DXB'): (430, 880),
    # Europe
    ('LOS', 'LHR'): (550, 1100),
    ('LOS', 'CDG'): (580, 1150),
    ('LOS', 'AMS'): (560, 1120),
    ('LOS', 'FRA'): (570, 1130),
    ('LOS', 'IST'): (480, 960),
    ('ABV', 'LHR'): (530, 1080),
    # Americas
    ('LOS', 'JFK'): (750, 1500),
    ('LOS', 'IAD'): (720, 1450),
    # Intra-Africa
    ('ACC', 'NBO'): (280, 560),
    ('ADD', 'JNB'): (300, 600),
    ('KGL', 'NBO'): (120, 240),
    ('DKR', 'ACC'): (180, 360),
}

CABINS = {
    'economy': 1.0,
    'premium_economy': 1.8,
    'business': 3.5,
    'first': 6.0,
}

STOPS = [
    {'stops': 0, 'label': 'Nonstop'},
    {'stops': 1, 'label': '1 Stop'},
    {'stops': 2, 'label': '2 Stops'},
]

OTA_PROVIDERS = [
    {'id': 'ota_1', 'name': 'TravelEase', 'trust_score': 4.8, 'verified': True, 'reviews': 12400},
    {'id': 'ota_2', 'name': 'FlyDirect', 'trust_score': 4.2, 'verified': True, 'reviews': 7300},
    {'id': 'ota_3', 'name': 'BudgetWings', 'trust_score': 3.5, 'verified': False, 'reviews': 2100},
]

# Module-level pricing constants — read once from Config at import time
from backend.config import Config as _Config
_MARKUP_MULT = _Config.MARKUP_PERCENT / 100
_SERVICE_FEE = _Config.SERVICE_FEE_USD
_COMMISSION_MULT = _Config.COMMISSION_PERCENT / 100

_CO2_CABIN_FACTOR = {'economy': 1.0, 'premium_economy': 1.5, 'business': 2.2, 'first': 3.0}

def _haversine_km(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    return R * 2 * math.asin(math.sqrt(a))

@lru_cache(maxsize=256)
def _estimate_co2(origin, destination, cabin):
    orig = AIRPORTS.get(origin, {})
    dest = AIRPORTS.get(destination, {})
    if 'lat' not in orig or 'lat' not in dest:
        return None
    dist = _haversine_km(orig['lat'], orig['lon'], dest['lat'], dest['lon'])
    factor = _CO2_CABIN_FACTOR.get(cabin, 1.0)
    return round(dist * 0.085 * factor)

def _get_price_prediction(departure_date_str, cabin, _now=None):
    now = _now or datetime.now()
    try:
        dep = datetime.strptime(departure_date_str, '%Y-%m-%d')
        days_out = (dep - now).days
    except Exception:
        return {'label': 'Stable', 'color': 'green', 'tip': 'Good time to book.'}
    if days_out < 0:
        return {'label': 'Departed', 'color': 'gray', 'tip': ''}
    if days_out < 7:
        return {'label': 'Rising Fast', 'color': 'red', 'tip': 'Last-minute premium applies. Book immediately.'}
    if days_out < 21:
        return {'label': 'Rising', 'color': 'orange', 'tip': 'Prices typically increase inside 3 weeks.'}
    if days_out > 120 and cabin == 'economy':
        return {'label': 'Drops Soon', 'color': 'blue', 'tip': 'Economy fares usually dip 6–8 weeks out.'}
    if dep.weekday() in (4, 5) and cabin in ('business', 'first'):
        return {'label': 'High Demand', 'color': 'orange', 'tip': 'Weekend premium cabin — book early.'}
    return {'label': 'Stable', 'color': 'green', 'tip': 'Good time to book.'}

def search_flights(origin, destination, departure_date, passengers=1, cabin='economy', return_date=None):
    origin = origin.upper()
    destination = destination.upper()
    key = (origin, destination)
    rev_key = (destination, origin)

    price_range = BASE_PRICES.get(key) or BASE_PRICES.get(rev_key)
    if not price_range:
        price_range = (300, 900)

    cabin_mult = CABINS.get(cabin, 1.0)

    # Pre-compute once — same for every flight on this route/date/cabin
    co2_per_pax = _estimate_co2(origin, destination, cabin)
    now = datetime.now()
    prediction = _get_price_prediction(departure_date, cabin, _now=now)
    origin_name = AIRPORTS.get(origin, {}).get('name', origin)
    dest_name = AIRPORTS.get(destination, {}).get('name', destination)

    results = []

    # Generate 3-6 flight options
    num_results = random.randint(3, 6)
    used_airlines = random.sample(AIRLINES, min(num_results, len(AIRLINES)))

    for i, airline in enumerate(used_airlines):
        base = round(random.uniform(price_range[0], price_range[1]) * cabin_mult, 2)
        stops_info = random.choice(STOPS) if i > 0 else STOPS[0]  # First result is nonstop

        dep_hour = random.randint(5, 22)
        dep_min = random.choice([0, 15, 30, 45])
        duration_hrs = _estimate_duration(origin, destination, stops_info['stops'])
        arr_hour = (dep_hour + duration_hrs) % 24

        flight_num = f"{airline['code']}{random.randint(100, 999)}"

        result = {
            'id': f"{flight_num}-{departure_date}-{i}",
            'airline': airline['name'],
            'airline_code': airline['code'],
            'airline_region': airline['region'],
            'flight_number': flight_num,
            'origin': origin,
            'destination': destination,
            'origin_airport': origin_name,
            'destination_airport': dest_name,
            'departure_date': departure_date,
            'departure_time': f"{dep_hour:02d}:{dep_min:02d}",
            'arrival_time': f"{arr_hour:02d}:{dep_min:02d}",
            'duration_hours': duration_hrs,
            'stops': stops_info['stops'],
            'stops_label': stops_info['label'],
            'cabin': cabin,
            'passengers': passengers,
            'is_africa_route': airline['region'] == 'africa',
            'airline_trust_score': airline['trust_score'],
            'pricing': _build_pricing(base, passengers),
            'ota_options': _get_ota_options(base, passengers),
            'available_seats': random.randint(3, 45),
            'baggage_included': cabin != 'economy',
            'co2_kg_per_pax': co2_per_pax,
            'price_prediction': prediction,
        }

        if return_date:
            ret_base = round(base * random.uniform(0.85, 1.15), 2)
            result['return_flight'] = {
                'date': return_date,
                'departure_time': f"{random.randint(6, 22):02d}:00",
                'pricing': _build_pricing(ret_base, passengers),
            }

        results.append(result)

    # Sort by total price ascending
    results.sort(key=lambda x: x['pricing']['total'])
    return results

def get_flight_by_id(flight_id):
    parts = flight_id.split('-')
    if len(parts) < 3:
        return None
    return {'id': flight_id, 'found': True}

def _build_pricing(base_usd, passengers):
    markup = round(base_usd * _MARKUP_MULT, 2)
    commission = round(base_usd * _COMMISSION_MULT, 2)
    subtotal = base_usd + markup + _SERVICE_FEE
    total = round(subtotal * passengers, 2)
    return {
        'base_fare': base_usd,
        'markup': markup,
        'service_fee': _SERVICE_FEE,
        'baggage_fee': 0,
        'seat_fee': 0,
        'commission': commission,
        'subtotal_per_pax': round(subtotal, 2),
        'total': total,
        'currency': 'USD',
        'per_passenger': round(subtotal, 2),
    }

def get_cheapest_price(origin, destination, departure_date, passengers=1, cabin='economy'):
    """Lightweight price-only lookup for flexible date grid — no full flight objects."""
    origin = origin.upper()
    destination = destination.upper()
    key = (origin, destination)
    price_range = BASE_PRICES.get(key) or BASE_PRICES.get((destination, origin)) or (300, 900)
    cabin_mult = CABINS.get(cabin, 1.0)
    base = random.uniform(price_range[0], price_range[1]) * cabin_mult
    markup = base * _MARKUP_MULT
    total = round((base + markup + _SERVICE_FEE) * passengers, 2)
    return total

def _get_ota_options(base, passengers):
    options = []
    for ota in OTA_PROVIDERS:
        # Each OTA has slight price variation
        variation = random.uniform(-0.03, 0.08)
        ota_price = round(base * (1 + variation) * passengers, 2)
        options.append({
            'ota_id': ota['id'],
            'ota_name': ota['name'],
            'trust_score': ota['trust_score'],
            'verified': ota['verified'],
            'reviews': ota['reviews'],
            'price': ota_price,
        })
    options.sort(key=lambda x: x['price'])
    return options

def _estimate_duration(origin, destination, stops):
    short_routes = {('LOS', 'ABV'), ('LOS', 'PHC'), ('ABV', 'PHC'), ('NBO', 'ADD'), ('KGL', 'NBO')}
    key = (origin.upper(), destination.upper())
    rev = (destination.upper(), origin.upper())
    if key in short_routes or rev in short_routes:
        base = 1
    elif origin in ('LOS', 'ABV') and destination in ('JFK', 'IAD', 'YYZ'):
        base = 10
    elif origin in ('LOS', 'ABV') and destination in ('LHR', 'CDG', 'AMS', 'FRA', 'IST'):
        base = 6
    elif origin in ('LOS', 'ABV') and destination in ('DXB', 'DOH'):
        base = 7
    else:
        base = 4
    return base + (stops * random.randint(1, 2))

def get_featured_routes():
    return [
        {'origin': 'LOS', 'destination': 'LHR', 'price_from': 549, 'airline': 'British Airways', 'label': 'Lagos → London'},
        {'origin': 'LOS', 'destination': 'DXB', 'price_from': 420, 'airline': 'Emirates', 'label': 'Lagos → Dubai'},
        {'origin': 'ABV', 'destination': 'NBO', 'price_from': 310, 'airline': 'Ethiopian Airlines', 'label': 'Abuja → Nairobi'},
        {'origin': 'LOS', 'destination': 'JFK', 'price_from': 720, 'airline': 'Air Peace', 'label': 'Lagos → New York'},
        {'origin': 'ACC', 'destination': 'ADD', 'price_from': 280, 'airline': 'RwandAir', 'label': 'Accra → Addis Ababa'},
        {'origin': 'NBO', 'destination': 'JNB', 'price_from': 240, 'airline': 'Kenya Airways', 'label': 'Nairobi → Johannesburg'},
    ]

def get_airports():
    return [{'code': k, **v} for k, v in AIRPORTS.items()]
