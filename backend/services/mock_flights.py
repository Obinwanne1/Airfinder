import random
from datetime import datetime, timedelta

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
    'LOS': {'name': 'Murtala Muhammed International', 'city': 'Lagos', 'country': 'Nigeria', 'region': 'africa'},
    'ABV': {'name': 'Nnamdi Azikiwe International', 'city': 'Abuja', 'country': 'Nigeria', 'region': 'africa'},
    'PHC': {'name': 'Port Harcourt International', 'city': 'Port Harcourt', 'country': 'Nigeria', 'region': 'africa'},
    'ACC': {'name': 'Kotoka International', 'city': 'Accra', 'country': 'Ghana', 'region': 'africa'},
    'NBO': {'name': 'Jomo Kenyatta International', 'city': 'Nairobi', 'country': 'Kenya', 'region': 'africa'},
    'ADD': {'name': 'Bole International', 'city': 'Addis Ababa', 'country': 'Ethiopia', 'region': 'africa'},
    'JNB': {'name': 'O.R. Tambo International', 'city': 'Johannesburg', 'country': 'South Africa', 'region': 'africa'},
    'CMN': {'name': 'Mohammed V International', 'city': 'Casablanca', 'country': 'Morocco', 'region': 'africa'},
    'KGL': {'name': 'Kigali International', 'city': 'Kigali', 'country': 'Rwanda', 'region': 'africa'},
    'DKR': {'name': 'Blaise Diagne International', 'city': 'Dakar', 'country': 'Senegal', 'region': 'africa'},
    'DXB': {'name': 'Dubai International', 'city': 'Dubai', 'country': 'UAE', 'region': 'middle_east'},
    'DOH': {'name': 'Hamad International', 'city': 'Doha', 'country': 'Qatar', 'region': 'middle_east'},
    'LHR': {'name': 'Heathrow Airport', 'city': 'London', 'country': 'UK', 'region': 'europe'},
    'CDG': {'name': 'Charles de Gaulle', 'city': 'Paris', 'country': 'France', 'region': 'europe'},
    'AMS': {'name': 'Amsterdam Schiphol', 'city': 'Amsterdam', 'country': 'Netherlands', 'region': 'europe'},
    'FRA': {'name': 'Frankfurt Airport', 'city': 'Frankfurt', 'country': 'Germany', 'region': 'europe'},
    'IST': {'name': 'Istanbul Airport', 'city': 'Istanbul', 'country': 'Turkey', 'region': 'europe'},
    'JFK': {'name': 'John F. Kennedy International', 'city': 'New York', 'country': 'USA', 'region': 'americas'},
    'IAD': {'name': 'Dulles International', 'city': 'Washington DC', 'country': 'USA', 'region': 'americas'},
    'YYZ': {'name': 'Toronto Pearson International', 'city': 'Toronto', 'country': 'Canada', 'region': 'americas'},
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

def search_flights(origin, destination, departure_date, passengers=1, cabin='economy', return_date=None):
    key = (origin.upper(), destination.upper())
    rev_key = (destination.upper(), origin.upper())

    price_range = BASE_PRICES.get(key) or BASE_PRICES.get(rev_key)
    if not price_range:
        # Generic range for unlisted routes
        price_range = (300, 900)

    cabin_mult = CABINS.get(cabin, 1.0)
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
            'origin': origin.upper(),
            'destination': destination.upper(),
            'origin_airport': AIRPORTS.get(origin.upper(), {}).get('name', origin),
            'destination_airport': AIRPORTS.get(destination.upper(), {}).get('name', destination),
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
    from backend.config import Config
    markup = round(base_usd * (Config.MARKUP_PERCENT / 100), 2)
    service_fee = Config.SERVICE_FEE_USD
    commission = round(base_usd * (Config.COMMISSION_PERCENT / 100), 2)
    subtotal = base_usd + markup + service_fee
    total = round(subtotal * passengers, 2)
    return {
        'base_fare': base_usd,
        'markup': markup,
        'service_fee': service_fee,
        'baggage_fee': 0,
        'seat_fee': 0,
        'commission': commission,
        'subtotal_per_pax': round(subtotal, 2),
        'total': total,
        'currency': 'USD',
        'per_passenger': round(subtotal, 2),
    }

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
