import math
import random
import time
from datetime import datetime, timedelta
from functools import lru_cache

AIRLINES = [
    # African carriers — operate within Africa and to/from Africa
    {'name': 'Air Peace', 'code': 'P4', 'region': 'africa', 'longhaul': False, 'trust_score': 4.1},
    {'name': 'Ethiopian Airlines', 'code': 'ET', 'region': 'africa', 'longhaul': True, 'trust_score': 4.7},
    {'name': 'Kenya Airways', 'code': 'KQ', 'region': 'africa', 'longhaul': True, 'trust_score': 4.3},
    {'name': 'RwandAir', 'code': 'WB', 'region': 'africa', 'longhaul': True, 'trust_score': 4.5},
    {'name': 'Arik Air', 'code': 'W3', 'region': 'africa', 'longhaul': False, 'trust_score': 3.8},
    {'name': 'IbomAir', 'code': 'Z9', 'region': 'africa', 'longhaul': False, 'trust_score': 4.0},
    {'name': 'South African Airways', 'code': 'SA', 'region': 'africa', 'longhaul': True, 'trust_score': 4.2},
    {'name': 'EgyptAir', 'code': 'MS', 'region': 'africa', 'longhaul': True, 'trust_score': 4.1},
    {'name': 'Royal Air Maroc', 'code': 'AT', 'region': 'africa', 'longhaul': True, 'trust_score': 4.0},
    {'name': 'Tunisair', 'code': 'TU', 'region': 'africa', 'longhaul': False, 'trust_score': 3.7},
    {'name': 'Air Côte d\'Ivoire', 'code': 'HF', 'region': 'africa', 'longhaul': False, 'trust_score': 3.9},
    {'name': 'ASKY Airlines', 'code': 'KP', 'region': 'africa', 'longhaul': False, 'trust_score': 3.8},
    # Middle Eastern carriers — fly globally, always eligible for any international route
    {'name': 'Emirates', 'code': 'EK', 'region': 'middle_east', 'longhaul': True, 'trust_score': 4.9},
    {'name': 'Qatar Airways', 'code': 'QR', 'region': 'middle_east', 'longhaul': True, 'trust_score': 4.8},
    {'name': 'Etihad Airways', 'code': 'EY', 'region': 'middle_east', 'longhaul': True, 'trust_score': 4.7},
    {'name': 'Turkish Airlines', 'code': 'TK', 'region': 'middle_east', 'longhaul': True, 'trust_score': 4.5},
    {'name': 'flydubai', 'code': 'FZ', 'region': 'middle_east', 'longhaul': False, 'trust_score': 4.2},
    # European carriers
    {'name': 'Lufthansa', 'code': 'LH', 'region': 'europe', 'longhaul': True, 'trust_score': 4.6},
    {'name': 'Eurowings', 'code': 'EW', 'region': 'europe', 'longhaul': False, 'trust_score': 4.0},
    {'name': 'British Airways', 'code': 'BA', 'region': 'europe', 'longhaul': True, 'trust_score': 4.6},
    {'name': 'Air France', 'code': 'AF', 'region': 'europe', 'longhaul': True, 'trust_score': 4.4},
    {'name': 'KLM', 'code': 'KL', 'region': 'europe', 'longhaul': True, 'trust_score': 4.5},
    {'name': 'Swiss International', 'code': 'LX', 'region': 'europe', 'longhaul': True, 'trust_score': 4.6},
    {'name': 'Austrian Airlines', 'code': 'OS', 'region': 'europe', 'longhaul': True, 'trust_score': 4.4},
    {'name': 'SAS', 'code': 'SK', 'region': 'europe', 'longhaul': True, 'trust_score': 4.3},
    {'name': 'Finnair', 'code': 'AY', 'region': 'europe', 'longhaul': True, 'trust_score': 4.4},
    {'name': 'TAP Air Portugal', 'code': 'TP', 'region': 'europe', 'longhaul': True, 'trust_score': 4.1},
    {'name': 'Iberia', 'code': 'IB', 'region': 'europe', 'longhaul': True, 'trust_score': 4.3},
    {'name': 'ITA Airways', 'code': 'AZ', 'region': 'europe', 'longhaul': True, 'trust_score': 3.9},
    {'name': 'Ryanair', 'code': 'FR', 'region': 'europe', 'longhaul': False, 'trust_score': 3.8},
    {'name': 'EasyJet', 'code': 'U2', 'region': 'europe', 'longhaul': False, 'trust_score': 3.9},
    {'name': 'Wizz Air', 'code': 'W6', 'region': 'europe', 'longhaul': False, 'trust_score': 3.7},
    {'name': 'LOT Polish Airlines', 'code': 'LO', 'region': 'europe', 'longhaul': True, 'trust_score': 4.2},
    # Asian carriers
    {'name': 'Singapore Airlines', 'code': 'SQ', 'region': 'asia', 'longhaul': True, 'trust_score': 4.9},
    {'name': 'Cathay Pacific', 'code': 'CX', 'region': 'asia', 'longhaul': True, 'trust_score': 4.8},
    {'name': 'Japan Airlines', 'code': 'JL', 'region': 'asia', 'longhaul': True, 'trust_score': 4.8},
    {'name': 'ANA', 'code': 'NH', 'region': 'asia', 'longhaul': True, 'trust_score': 4.8},
    {'name': 'Korean Air', 'code': 'KE', 'region': 'asia', 'longhaul': True, 'trust_score': 4.6},
    {'name': 'Air India', 'code': 'AI', 'region': 'asia', 'longhaul': True, 'trust_score': 3.9},
    {'name': 'IndiGo', 'code': '6E', 'region': 'asia', 'longhaul': False, 'trust_score': 4.0},
    {'name': 'Malaysia Airlines', 'code': 'MH', 'region': 'asia', 'longhaul': True, 'trust_score': 4.4},
    {'name': 'Thai Airways', 'code': 'TG', 'region': 'asia', 'longhaul': True, 'trust_score': 4.3},
    {'name': 'Garuda Indonesia', 'code': 'GA', 'region': 'asia', 'longhaul': True, 'trust_score': 4.2},
    # Americas carriers
    {'name': 'Delta Air Lines', 'code': 'DL', 'region': 'americas', 'longhaul': True, 'trust_score': 4.5},
    {'name': 'United Airlines', 'code': 'UA', 'region': 'americas', 'longhaul': True, 'trust_score': 4.4},
    {'name': 'American Airlines', 'code': 'AA', 'region': 'americas', 'longhaul': True, 'trust_score': 4.3},
    {'name': 'Air Canada', 'code': 'AC', 'region': 'americas', 'longhaul': True, 'trust_score': 4.4},
    {'name': 'LATAM Airlines', 'code': 'LA', 'region': 'americas', 'longhaul': True, 'trust_score': 4.2},
    # Oceania carriers
    {'name': 'Qantas', 'code': 'QF', 'region': 'oceania', 'longhaul': True, 'trust_score': 4.7},
    {'name': 'Air New Zealand', 'code': 'NZ', 'region': 'oceania', 'longhaul': True, 'trust_score': 4.7},
]

def _apply_airport_restrictions(pool, origin, destination):
    """Narrow airline pool to carriers that actually serve these specific airports."""
    dest_w = AIRPORT_CARRIERS.get(destination)
    orig_w = AIRPORT_CARRIERS.get(origin)
    if not dest_w and not orig_w:
        return pool
    if dest_w and orig_w:
        intersect = [a for a in pool if a['name'] in dest_w and a['name'] in orig_w]
        if len(intersect) >= 2:
            return intersect
        dest_only = [a for a in pool if a['name'] in dest_w]
        return dest_only if len(dest_only) >= 2 else pool
    whitelist = dest_w or orig_w
    restricted = [a for a in pool if a['name'] in whitelist]
    return restricted if len(restricted) >= 2 else pool

def _eligible_airlines(origin_region, dest_region):
    """Return airlines that plausibly operate a route between these two regions."""
    same_region = origin_region == dest_region
    eligible = []
    for a in AIRLINES:
        r = a['region']
        if same_region:
            # Short/medium-haul intra-region: any airline from that region
            if r == origin_region:
                eligible.append(a)
        else:
            # Cross-region: airlines from either endpoint region (if longhaul capable)
            # plus all Middle Eastern carriers (universal connectors)
            if r == 'middle_east':
                eligible.append(a)
            elif r in (origin_region, dest_region) and a['longhaul']:
                eligible.append(a)
    # Fallback: if pool too small, add any longhaul airline
    if len(eligible) < 4:
        for a in AIRLINES:
            if a['longhaul'] and a not in eligible:
                eligible.append(a)
    return eligible

AIRPORTS = {
    # ── Nigeria ──
    'LOS': {'name': 'Murtala Muhammed International', 'city': 'Lagos', 'country': 'Nigeria', 'region': 'africa', 'lat': 6.5774, 'lon': 3.3210},
    'ABV': {'name': 'Nnamdi Azikiwe International', 'city': 'Abuja', 'country': 'Nigeria', 'region': 'africa', 'lat': 9.0064, 'lon': 7.2632},
    'PHC': {'name': 'Port Harcourt International', 'city': 'Port Harcourt', 'country': 'Nigeria', 'region': 'africa', 'lat': 5.0155, 'lon': 6.9496},
    'KAN': {'name': 'Mallam Aminu Kano International', 'city': 'Kano', 'country': 'Nigeria', 'region': 'africa', 'lat': 12.0476, 'lon': 8.5246},
    'ENU': {'name': 'Akanu Ibiam International', 'city': 'Enugu', 'country': 'Nigeria', 'region': 'africa', 'lat': 6.4743, 'lon': 7.5620},
    # ── West Africa ──
    'ACC': {'name': 'Kotoka International', 'city': 'Accra', 'country': 'Ghana', 'region': 'africa', 'lat': 5.6052, 'lon': -0.1668},
    'DKR': {'name': 'Blaise Diagne International', 'city': 'Dakar', 'country': 'Senegal', 'region': 'africa', 'lat': 14.6736, 'lon': -17.4900},
    'ABJ': {'name': 'Félix Houphouët-Boigny International', 'city': 'Abidjan', 'country': 'Côte d\'Ivoire', 'region': 'africa', 'lat': 5.2613, 'lon': -3.9262},
    'LFW': {'name': 'Gnassingbé Eyadéma International', 'city': 'Lomé', 'country': 'Togo', 'region': 'africa', 'lat': 6.1657, 'lon': 1.2545},
    'COO': {'name': 'Cadjehoun Airport', 'city': 'Cotonou', 'country': 'Benin', 'region': 'africa', 'lat': 6.3572, 'lon': 2.3845},
    'OUA': {'name': 'Ouagadougou Airport', 'city': 'Ouagadougou', 'country': 'Burkina Faso', 'region': 'africa', 'lat': 12.3532, 'lon': -1.5124},
    'BKO': {'name': 'Bamako-Sénou International', 'city': 'Bamako', 'country': 'Mali', 'region': 'africa', 'lat': 12.5335, 'lon': -7.9499},
    'CKY': {'name': 'Conakry International', 'city': 'Conakry', 'country': 'Guinea', 'region': 'africa', 'lat': 9.5769, 'lon': -13.6120},
    'DLA': {'name': 'Douala International', 'city': 'Douala', 'country': 'Cameroon', 'region': 'africa', 'lat': 4.0061, 'lon': 9.7195},
    # ── East Africa ──
    'NBO': {'name': 'Jomo Kenyatta International', 'city': 'Nairobi', 'country': 'Kenya', 'region': 'africa', 'lat': -1.3192, 'lon': 36.9275},
    'ADD': {'name': 'Bole International', 'city': 'Addis Ababa', 'country': 'Ethiopia', 'region': 'africa', 'lat': 8.9779, 'lon': 38.7993},
    'KGL': {'name': 'Kigali International', 'city': 'Kigali', 'country': 'Rwanda', 'region': 'africa', 'lat': -1.9686, 'lon': 30.1395},
    'EBB': {'name': 'Entebbe International', 'city': 'Kampala', 'country': 'Uganda', 'region': 'africa', 'lat': 0.0424, 'lon': 32.4435},
    'DAR': {'name': 'Julius Nyerere International', 'city': 'Dar es Salaam', 'country': 'Tanzania', 'region': 'africa', 'lat': -6.8781, 'lon': 39.2026},
    'JRO': {'name': 'Kilimanjaro International', 'city': 'Kilimanjaro', 'country': 'Tanzania', 'region': 'africa', 'lat': -3.4294, 'lon': 37.0745},
    # ── Southern Africa ──
    'JNB': {'name': 'O.R. Tambo International', 'city': 'Johannesburg', 'country': 'South Africa', 'region': 'africa', 'lat': -26.1367, 'lon': 28.2411},
    'CPT': {'name': 'Cape Town International', 'city': 'Cape Town', 'country': 'South Africa', 'region': 'africa', 'lat': -33.9648, 'lon': 18.6017},
    'DUR': {'name': 'King Shaka International', 'city': 'Durban', 'country': 'South Africa', 'region': 'africa', 'lat': -29.6144, 'lon': 31.1197},
    'MPM': {'name': 'Maputo International', 'city': 'Maputo', 'country': 'Mozambique', 'region': 'africa', 'lat': -25.9208, 'lon': 32.5726},
    'MRU': {'name': 'Sir Seewoosagur Ramgoolam International', 'city': 'Mauritius', 'country': 'Mauritius', 'region': 'africa', 'lat': -20.4302, 'lon': 57.6836},
    # ── North Africa ──
    'CMN': {'name': 'Mohammed V International', 'city': 'Casablanca', 'country': 'Morocco', 'region': 'africa', 'lat': 33.3675, 'lon': -7.5898},
    'RAK': {'name': 'Marrakesh Menara Airport', 'city': 'Marrakesh', 'country': 'Morocco', 'region': 'africa', 'lat': 31.6069, 'lon': -8.0363},
    'TUN': {'name': 'Tunis-Carthage International', 'city': 'Tunis', 'country': 'Tunisia', 'region': 'africa', 'lat': 36.8510, 'lon': 10.2272},
    'ALG': {'name': 'Houari Boumediene Airport', 'city': 'Algiers', 'country': 'Algeria', 'region': 'africa', 'lat': 36.6910, 'lon': 3.2154},
    'CAI': {'name': 'Cairo International', 'city': 'Cairo', 'country': 'Egypt', 'region': 'africa', 'lat': 30.1219, 'lon': 31.4056},
    # ── Middle East ──
    'DXB': {'name': 'Dubai International', 'city': 'Dubai', 'country': 'UAE', 'region': 'middle_east', 'lat': 25.2532, 'lon': 55.3657},
    'AUH': {'name': 'Abu Dhabi International', 'city': 'Abu Dhabi', 'country': 'UAE', 'region': 'middle_east', 'lat': 24.4330, 'lon': 54.6511},
    'DOH': {'name': 'Hamad International', 'city': 'Doha', 'country': 'Qatar', 'region': 'middle_east', 'lat': 25.2609, 'lon': 51.6138},
    'RUH': {'name': 'King Khalid International', 'city': 'Riyadh', 'country': 'Saudi Arabia', 'region': 'middle_east', 'lat': 24.9578, 'lon': 46.6989},
    'JED': {'name': 'King Abdulaziz International', 'city': 'Jeddah', 'country': 'Saudi Arabia', 'region': 'middle_east', 'lat': 21.6796, 'lon': 39.1565},
    'KWI': {'name': 'Kuwait International', 'city': 'Kuwait City', 'country': 'Kuwait', 'region': 'middle_east', 'lat': 29.2267, 'lon': 47.9689},
    'BAH': {'name': 'Bahrain International', 'city': 'Manama', 'country': 'Bahrain', 'region': 'middle_east', 'lat': 26.2708, 'lon': 50.6336},
    'MCT': {'name': 'Muscat International', 'city': 'Muscat', 'country': 'Oman', 'region': 'middle_east', 'lat': 23.5933, 'lon': 58.2844},
    'AMM': {'name': 'Queen Alia International', 'city': 'Amman', 'country': 'Jordan', 'region': 'middle_east', 'lat': 31.7226, 'lon': 35.9932},
    'BEY': {'name': 'Beirut Rafic Hariri International', 'city': 'Beirut', 'country': 'Lebanon', 'region': 'middle_east', 'lat': 33.8209, 'lon': 35.4884},
    'TLV': {'name': 'Ben Gurion International', 'city': 'Tel Aviv', 'country': 'Israel', 'region': 'middle_east', 'lat': 32.0114, 'lon': 34.8867},
    'IST': {'name': 'Istanbul Airport', 'city': 'Istanbul', 'country': 'Turkey', 'region': 'europe', 'lat': 41.2608, 'lon': 28.7419},
    'SAW': {'name': 'Istanbul Sabiha Gökçen', 'city': 'Istanbul', 'country': 'Turkey', 'region': 'europe', 'lat': 40.8983, 'lon': 29.3092},
    'AYT': {'name': 'Antalya Airport', 'city': 'Antalya', 'country': 'Turkey', 'region': 'europe', 'lat': 36.8987, 'lon': 30.8005},
    # ── Germany ──
    'FRA': {'name': 'Frankfurt Airport', 'city': 'Frankfurt', 'country': 'Germany', 'region': 'europe', 'lat': 50.0379, 'lon': 8.5622},
    'MUC': {'name': 'Munich Airport', 'city': 'Munich', 'country': 'Germany', 'region': 'europe', 'lat': 48.3537, 'lon': 11.7750},
    'DUS': {'name': 'Düsseldorf Airport', 'city': 'Düsseldorf', 'country': 'Germany', 'region': 'europe', 'lat': 51.2895, 'lon': 6.7668},
    'BER': {'name': 'Berlin Brandenburg Airport', 'city': 'Berlin', 'country': 'Germany', 'region': 'europe', 'lat': 52.3667, 'lon': 13.5033},
    'HAM': {'name': 'Hamburg Airport', 'city': 'Hamburg', 'country': 'Germany', 'region': 'europe', 'lat': 53.6304, 'lon': 9.9882},
    'STR': {'name': 'Stuttgart Airport', 'city': 'Stuttgart', 'country': 'Germany', 'region': 'europe', 'lat': 48.6899, 'lon': 9.2220},
    'CGN': {'name': 'Cologne Bonn Airport', 'city': 'Cologne', 'country': 'Germany', 'region': 'europe', 'lat': 50.8659, 'lon': 7.1427},
    'NUE': {'name': 'Nuremberg Airport', 'city': 'Nuremberg', 'country': 'Germany', 'region': 'europe', 'lat': 49.4987, 'lon': 11.0669},
    'HAJ': {'name': 'Hannover Airport', 'city': 'Hannover', 'country': 'Germany', 'region': 'europe', 'lat': 52.4611, 'lon': 9.6850},
    'LEJ': {'name': 'Leipzig/Halle Airport', 'city': 'Leipzig', 'country': 'Germany', 'region': 'europe', 'lat': 51.4324, 'lon': 12.2416},
    'DRS': {'name': 'Dresden Airport', 'city': 'Dresden', 'country': 'Germany', 'region': 'europe', 'lat': 51.1328, 'lon': 13.7672},
    'BSL': {'name': 'EuroAirport Basel-Mulhouse-Freiburg', 'city': 'Basel', 'country': 'Germany/France', 'region': 'europe', 'lat': 47.5996, 'lon': 7.5290},
    'FKB': {'name': 'Karlsruhe/Baden-Baden Airport', 'city': 'Karlsruhe', 'country': 'Germany', 'region': 'europe', 'lat': 48.7793, 'lon': 8.0805},
    # ── UK ──
    'LHR': {'name': 'Heathrow Airport', 'city': 'London', 'country': 'UK', 'region': 'europe', 'lat': 51.4700, 'lon': -0.4543},
    'LGW': {'name': 'London Gatwick', 'city': 'London', 'country': 'UK', 'region': 'europe', 'lat': 51.1537, 'lon': -0.1821},
    'STN': {'name': 'London Stansted', 'city': 'London', 'country': 'UK', 'region': 'europe', 'lat': 51.8860, 'lon': 0.2389},
    'MAN': {'name': 'Manchester Airport', 'city': 'Manchester', 'country': 'UK', 'region': 'europe', 'lat': 53.3537, 'lon': -2.2750},
    'EDI': {'name': 'Edinburgh Airport', 'city': 'Edinburgh', 'country': 'UK', 'region': 'europe', 'lat': 55.9500, 'lon': -3.3725},
    'BHX': {'name': 'Birmingham Airport', 'city': 'Birmingham', 'country': 'UK', 'region': 'europe', 'lat': 52.4539, 'lon': -1.7480},
    'GLA': {'name': 'Glasgow Airport', 'city': 'Glasgow', 'country': 'UK', 'region': 'europe', 'lat': 55.8719, 'lon': -4.4330},
    # ── France ──
    'CDG': {'name': 'Charles de Gaulle', 'city': 'Paris', 'country': 'France', 'region': 'europe', 'lat': 49.0097, 'lon': 2.5479},
    'ORY': {'name': 'Paris Orly', 'city': 'Paris', 'country': 'France', 'region': 'europe', 'lat': 48.7233, 'lon': 2.3794},
    'NCE': {'name': 'Nice Côte d\'Azur', 'city': 'Nice', 'country': 'France', 'region': 'europe', 'lat': 43.6584, 'lon': 7.2159},
    'LYS': {'name': 'Lyon Saint-Exupéry', 'city': 'Lyon', 'country': 'France', 'region': 'europe', 'lat': 45.7256, 'lon': 5.0811},
    'MRS': {'name': 'Marseille Provence', 'city': 'Marseille', 'country': 'France', 'region': 'europe', 'lat': 43.4393, 'lon': 5.2214},
    'BOD': {'name': 'Bordeaux-Mérignac', 'city': 'Bordeaux', 'country': 'France', 'region': 'europe', 'lat': 44.8283, 'lon': -0.7156},
    # ── Netherlands ──
    'AMS': {'name': 'Amsterdam Schiphol', 'city': 'Amsterdam', 'country': 'Netherlands', 'region': 'europe', 'lat': 52.3086, 'lon': 4.7639},
    'EIN': {'name': 'Eindhoven Airport', 'city': 'Eindhoven', 'country': 'Netherlands', 'region': 'europe', 'lat': 51.4501, 'lon': 5.3746},
    # ── Belgium ──
    'BRU': {'name': 'Brussels Airport', 'city': 'Brussels', 'country': 'Belgium', 'region': 'europe', 'lat': 50.9014, 'lon': 4.4844},
    'CRL': {'name': 'Brussels South Charleroi', 'city': 'Charleroi', 'country': 'Belgium', 'region': 'europe', 'lat': 50.4592, 'lon': 4.4538},
    # ── Switzerland ──
    'ZRH': {'name': 'Zurich Airport', 'city': 'Zurich', 'country': 'Switzerland', 'region': 'europe', 'lat': 47.4647, 'lon': 8.5492},
    'GVA': {'name': 'Geneva Airport', 'city': 'Geneva', 'country': 'Switzerland', 'region': 'europe', 'lat': 46.2381, 'lon': 6.1089},
    # ── Austria ──
    'VIE': {'name': 'Vienna International', 'city': 'Vienna', 'country': 'Austria', 'region': 'europe', 'lat': 48.1103, 'lon': 16.5697},
    'SZG': {'name': 'Salzburg Airport', 'city': 'Salzburg', 'country': 'Austria', 'region': 'europe', 'lat': 47.7933, 'lon': 13.0043},
    # ── Spain ──
    'MAD': {'name': 'Adolfo Suárez Madrid-Barajas', 'city': 'Madrid', 'country': 'Spain', 'region': 'europe', 'lat': 40.4936, 'lon': -3.5668},
    'BCN': {'name': 'Barcelona El Prat', 'city': 'Barcelona', 'country': 'Spain', 'region': 'europe', 'lat': 41.2971, 'lon': 2.0785},
    'PMI': {'name': 'Palma de Mallorca Airport', 'city': 'Palma', 'country': 'Spain', 'region': 'europe', 'lat': 39.5517, 'lon': 2.7388},
    'AGP': {'name': 'Málaga Airport', 'city': 'Málaga', 'country': 'Spain', 'region': 'europe', 'lat': 36.6749, 'lon': -4.4991},
    'ALC': {'name': 'Alicante Airport', 'city': 'Alicante', 'country': 'Spain', 'region': 'europe', 'lat': 38.2822, 'lon': -0.5582},
    'VLC': {'name': 'Valencia Airport', 'city': 'Valencia', 'country': 'Spain', 'region': 'europe', 'lat': 39.4893, 'lon': -0.4816},
    'SVQ': {'name': 'Sevilla Airport', 'city': 'Seville', 'country': 'Spain', 'region': 'europe', 'lat': 37.4180, 'lon': -5.8931},
    # ── Portugal ──
    'LIS': {'name': 'Humberto Delgado Airport', 'city': 'Lisbon', 'country': 'Portugal', 'region': 'europe', 'lat': 38.7742, 'lon': -9.1342},
    'OPO': {'name': 'Francisco de Sá Carneiro Airport', 'city': 'Porto', 'country': 'Portugal', 'region': 'europe', 'lat': 41.2481, 'lon': -8.6814},
    'FAO': {'name': 'Faro Airport', 'city': 'Faro', 'country': 'Portugal', 'region': 'europe', 'lat': 37.0144, 'lon': -7.9659},
    # ── Italy ──
    'FCO': {'name': 'Rome Fiumicino', 'city': 'Rome', 'country': 'Italy', 'region': 'europe', 'lat': 41.8003, 'lon': 12.2389},
    'MXP': {'name': 'Milan Malpensa', 'city': 'Milan', 'country': 'Italy', 'region': 'europe', 'lat': 45.6306, 'lon': 8.7281},
    'BGY': {'name': 'Milan Bergamo Orio al Serio', 'city': 'Milan', 'country': 'Italy', 'region': 'europe', 'lat': 45.6739, 'lon': 9.7042},
    'VCE': {'name': 'Venice Marco Polo', 'city': 'Venice', 'country': 'Italy', 'region': 'europe', 'lat': 45.5053, 'lon': 12.3519},
    'NAP': {'name': 'Naples International', 'city': 'Naples', 'country': 'Italy', 'region': 'europe', 'lat': 40.8860, 'lon': 14.2908},
    'CTA': {'name': 'Catania-Fontanarossa', 'city': 'Catania', 'country': 'Italy', 'region': 'europe', 'lat': 37.4668, 'lon': 15.0664},
    # ── Scandinavia ──
    'CPH': {'name': 'Copenhagen Airport', 'city': 'Copenhagen', 'country': 'Denmark', 'region': 'europe', 'lat': 55.6180, 'lon': 12.6508},
    'ARN': {'name': 'Stockholm Arlanda', 'city': 'Stockholm', 'country': 'Sweden', 'region': 'europe', 'lat': 59.6519, 'lon': 17.9186},
    'OSL': {'name': 'Oslo Gardermoen', 'city': 'Oslo', 'country': 'Norway', 'region': 'europe', 'lat': 60.1976, 'lon': 11.1004},
    'HEL': {'name': 'Helsinki-Vantaa', 'city': 'Helsinki', 'country': 'Finland', 'region': 'europe', 'lat': 60.3172, 'lon': 24.9633},
    'GOT': {'name': 'Gothenburg Landvetter', 'city': 'Gothenburg', 'country': 'Sweden', 'region': 'europe', 'lat': 57.6628, 'lon': 12.2798},
    # ── Eastern Europe ──
    'WAW': {'name': 'Warsaw Chopin Airport', 'city': 'Warsaw', 'country': 'Poland', 'region': 'europe', 'lat': 52.1657, 'lon': 20.9671},
    'KRK': {'name': 'Kraków John Paul II International', 'city': 'Kraków', 'country': 'Poland', 'region': 'europe', 'lat': 50.0777, 'lon': 19.7848},
    'PRG': {'name': 'Václav Havel Airport Prague', 'city': 'Prague', 'country': 'Czech Republic', 'region': 'europe', 'lat': 50.1008, 'lon': 14.2600},
    'BUD': {'name': 'Budapest Ferenc Liszt International', 'city': 'Budapest', 'country': 'Hungary', 'region': 'europe', 'lat': 47.4298, 'lon': 19.2611},
    'OTP': {'name': 'Henri Coandă International', 'city': 'Bucharest', 'country': 'Romania', 'region': 'europe', 'lat': 44.5711, 'lon': 26.0850},
    'SOF': {'name': 'Sofia Airport', 'city': 'Sofia', 'country': 'Bulgaria', 'region': 'europe', 'lat': 42.6952, 'lon': 23.4114},
    'ZAG': {'name': 'Zagreb Airport', 'city': 'Zagreb', 'country': 'Croatia', 'region': 'europe', 'lat': 45.7429, 'lon': 16.0688},
    'SPU': {'name': 'Split Airport', 'city': 'Split', 'country': 'Croatia', 'region': 'europe', 'lat': 43.5389, 'lon': 16.2980},
    'DBV': {'name': 'Dubrovnik Airport', 'city': 'Dubrovnik', 'country': 'Croatia', 'region': 'europe', 'lat': 42.5614, 'lon': 18.2682},
    'KBP': {'name': 'Kyiv Boryspil International', 'city': 'Kyiv', 'country': 'Ukraine', 'region': 'europe', 'lat': 50.3450, 'lon': 30.8947},
    'RIX': {'name': 'Riga International', 'city': 'Riga', 'country': 'Latvia', 'region': 'europe', 'lat': 56.9236, 'lon': 23.9711},
    'TLL': {'name': 'Tallinn Airport', 'city': 'Tallinn', 'country': 'Estonia', 'region': 'europe', 'lat': 59.4133, 'lon': 24.8328},
    'VNO': {'name': 'Vilnius Airport', 'city': 'Vilnius', 'country': 'Lithuania', 'region': 'europe', 'lat': 54.6341, 'lon': 25.2858},
    'SKP': {'name': 'Skopje International', 'city': 'Skopje', 'country': 'North Macedonia', 'region': 'europe', 'lat': 41.9616, 'lon': 21.6214},
    'TIA': {'name': 'Tirana International', 'city': 'Tirana', 'country': 'Albania', 'region': 'europe', 'lat': 41.4147, 'lon': 19.7206},
    # ── Greece ──
    'ATH': {'name': 'Athens Eleftherios Venizelos', 'city': 'Athens', 'country': 'Greece', 'region': 'europe', 'lat': 37.9364, 'lon': 23.9445},
    'HER': {'name': 'Heraklion International', 'city': 'Heraklion', 'country': 'Greece', 'region': 'europe', 'lat': 35.3397, 'lon': 25.1803},
    'CFU': {'name': 'Corfu International', 'city': 'Corfu', 'country': 'Greece', 'region': 'europe', 'lat': 39.6019, 'lon': 19.9117},
    'RHO': {'name': 'Rhodes International', 'city': 'Rhodes', 'country': 'Greece', 'region': 'europe', 'lat': 36.4054, 'lon': 28.0862},
    # ── Americas ──
    'JFK': {'name': 'John F. Kennedy International', 'city': 'New York', 'country': 'USA', 'region': 'americas', 'lat': 40.6413, 'lon': -73.7781},
    'EWR': {'name': 'Newark Liberty International', 'city': 'Newark', 'country': 'USA', 'region': 'americas', 'lat': 40.6895, 'lon': -74.1745},
    'LGA': {'name': 'LaGuardia Airport', 'city': 'New York', 'country': 'USA', 'region': 'americas', 'lat': 40.7772, 'lon': -73.8726},
    'IAD': {'name': 'Dulles International', 'city': 'Washington DC', 'country': 'USA', 'region': 'americas', 'lat': 38.9531, 'lon': -77.4565},
    'DCA': {'name': 'Ronald Reagan National', 'city': 'Washington DC', 'country': 'USA', 'region': 'americas', 'lat': 38.8521, 'lon': -77.0377},
    'ORD': {'name': 'Chicago O\'Hare International', 'city': 'Chicago', 'country': 'USA', 'region': 'americas', 'lat': 41.9742, 'lon': -87.9073},
    'MDW': {'name': 'Chicago Midway', 'city': 'Chicago', 'country': 'USA', 'region': 'americas', 'lat': 41.7868, 'lon': -87.7522},
    'ATL': {'name': 'Hartsfield-Jackson Atlanta International', 'city': 'Atlanta', 'country': 'USA', 'region': 'americas', 'lat': 33.6407, 'lon': -84.4277},
    'MIA': {'name': 'Miami International', 'city': 'Miami', 'country': 'USA', 'region': 'americas', 'lat': 25.7959, 'lon': -80.2870},
    'FLL': {'name': 'Fort Lauderdale-Hollywood International', 'city': 'Fort Lauderdale', 'country': 'USA', 'region': 'americas', 'lat': 26.0726, 'lon': -80.1527},
    'BOS': {'name': 'Boston Logan International', 'city': 'Boston', 'country': 'USA', 'region': 'americas', 'lat': 42.3656, 'lon': -71.0096},
    'DFW': {'name': 'Dallas/Fort Worth International', 'city': 'Dallas', 'country': 'USA', 'region': 'americas', 'lat': 32.8998, 'lon': -97.0403},
    'LAX': {'name': 'Los Angeles International', 'city': 'Los Angeles', 'country': 'USA', 'region': 'americas', 'lat': 33.9425, 'lon': -118.4081},
    'SFO': {'name': 'San Francisco International', 'city': 'San Francisco', 'country': 'USA', 'region': 'americas', 'lat': 37.6213, 'lon': -122.3790},
    'SEA': {'name': 'Seattle-Tacoma International', 'city': 'Seattle', 'country': 'USA', 'region': 'americas', 'lat': 47.4502, 'lon': -122.3088},
    'LAS': {'name': 'Harry Reid International', 'city': 'Las Vegas', 'country': 'USA', 'region': 'americas', 'lat': 36.0840, 'lon': -115.1537},
    'PHX': {'name': 'Phoenix Sky Harbor International', 'city': 'Phoenix', 'country': 'USA', 'region': 'americas', 'lat': 33.4373, 'lon': -112.0078},
    'DEN': {'name': 'Denver International', 'city': 'Denver', 'country': 'USA', 'region': 'americas', 'lat': 39.8561, 'lon': -104.6737},
    'MSP': {'name': 'Minneapolis-Saint Paul International', 'city': 'Minneapolis', 'country': 'USA', 'region': 'americas', 'lat': 44.8820, 'lon': -93.2218},
    'DTW': {'name': 'Detroit Metropolitan Wayne County', 'city': 'Detroit', 'country': 'USA', 'region': 'americas', 'lat': 42.2124, 'lon': -83.3534},
    'YYZ': {'name': 'Toronto Pearson International', 'city': 'Toronto', 'country': 'Canada', 'region': 'americas', 'lat': 43.6777, 'lon': -79.6248},
    'YVR': {'name': 'Vancouver International', 'city': 'Vancouver', 'country': 'Canada', 'region': 'americas', 'lat': 49.1967, 'lon': -123.1815},
    'YUL': {'name': 'Montréal-Trudeau International', 'city': 'Montreal', 'country': 'Canada', 'region': 'americas', 'lat': 45.4706, 'lon': -73.7408},
    'YYC': {'name': 'Calgary International', 'city': 'Calgary', 'country': 'Canada', 'region': 'americas', 'lat': 51.1215, 'lon': -114.0130},
    'MEX': {'name': 'Benito Juárez International', 'city': 'Mexico City', 'country': 'Mexico', 'region': 'americas', 'lat': 19.4363, 'lon': -99.0721},
    'CUN': {'name': 'Cancún International', 'city': 'Cancún', 'country': 'Mexico', 'region': 'americas', 'lat': 21.0365, 'lon': -86.8771},
    'GRU': {'name': 'São Paulo/Guarulhos International', 'city': 'São Paulo', 'country': 'Brazil', 'region': 'americas', 'lat': -23.4356, 'lon': -46.4731},
    'GIG': {'name': 'Rio de Janeiro/Galeão International', 'city': 'Rio de Janeiro', 'country': 'Brazil', 'region': 'americas', 'lat': -22.8099, 'lon': -43.2506},
    'EZE': {'name': 'Ministro Pistarini International', 'city': 'Buenos Aires', 'country': 'Argentina', 'region': 'americas', 'lat': -34.8222, 'lon': -58.5358},
    'SCL': {'name': 'Arturo Merino Benítez International', 'city': 'Santiago', 'country': 'Chile', 'region': 'americas', 'lat': -33.3930, 'lon': -70.7858},
    'BOG': {'name': 'El Dorado International', 'city': 'Bogotá', 'country': 'Colombia', 'region': 'americas', 'lat': 4.7016, 'lon': -74.1469},
    'LIM': {'name': 'Jorge Chávez International', 'city': 'Lima', 'country': 'Peru', 'region': 'americas', 'lat': -12.0219, 'lon': -77.1143},
    'PTY': {'name': 'Tocumen International', 'city': 'Panama City', 'country': 'Panama', 'region': 'americas', 'lat': 9.0714, 'lon': -79.3835},
    # ── Asia ──
    'SIN': {'name': 'Singapore Changi', 'city': 'Singapore', 'country': 'Singapore', 'region': 'asia', 'lat': 1.3644, 'lon': 103.9915},
    'BKK': {'name': 'Suvarnabhumi Airport', 'city': 'Bangkok', 'country': 'Thailand', 'region': 'asia', 'lat': 13.6900, 'lon': 100.7501},
    'DMK': {'name': 'Don Mueang International', 'city': 'Bangkok', 'country': 'Thailand', 'region': 'asia', 'lat': 13.9126, 'lon': 100.6067},
    'KUL': {'name': 'Kuala Lumpur International', 'city': 'Kuala Lumpur', 'country': 'Malaysia', 'region': 'asia', 'lat': 2.7456, 'lon': 101.7099},
    'CGK': {'name': 'Soekarno-Hatta International', 'city': 'Jakarta', 'country': 'Indonesia', 'region': 'asia', 'lat': -6.1275, 'lon': 106.6537},
    'HKG': {'name': 'Hong Kong International', 'city': 'Hong Kong', 'country': 'Hong Kong', 'region': 'asia', 'lat': 22.3080, 'lon': 113.9185},
    'PVG': {'name': 'Shanghai Pudong International', 'city': 'Shanghai', 'country': 'China', 'region': 'asia', 'lat': 31.1443, 'lon': 121.8083},
    'SHA': {'name': 'Shanghai Hongqiao International', 'city': 'Shanghai', 'country': 'China', 'region': 'asia', 'lat': 31.1979, 'lon': 121.3363},
    'PEK': {'name': 'Beijing Capital International', 'city': 'Beijing', 'country': 'China', 'region': 'asia', 'lat': 40.0799, 'lon': 116.6031},
    'PKX': {'name': 'Beijing Daxing International', 'city': 'Beijing', 'country': 'China', 'region': 'asia', 'lat': 39.5095, 'lon': 116.4105},
    'CAN': {'name': 'Guangzhou Baiyun International', 'city': 'Guangzhou', 'country': 'China', 'region': 'asia', 'lat': 23.3924, 'lon': 113.2990},
    'ICN': {'name': 'Incheon International', 'city': 'Seoul', 'country': 'South Korea', 'region': 'asia', 'lat': 37.4602, 'lon': 126.4407},
    'GMP': {'name': 'Gimpo International', 'city': 'Seoul', 'country': 'South Korea', 'region': 'asia', 'lat': 37.5583, 'lon': 126.7906},
    'NRT': {'name': 'Narita International', 'city': 'Tokyo', 'country': 'Japan', 'region': 'asia', 'lat': 35.7647, 'lon': 140.3864},
    'HND': {'name': 'Tokyo Haneda', 'city': 'Tokyo', 'country': 'Japan', 'region': 'asia', 'lat': 35.5494, 'lon': 139.7798},
    'KIX': {'name': 'Kansai International', 'city': 'Osaka', 'country': 'Japan', 'region': 'asia', 'lat': 34.4273, 'lon': 135.2440},
    'DEL': {'name': 'Indira Gandhi International', 'city': 'New Delhi', 'country': 'India', 'region': 'asia', 'lat': 28.5561, 'lon': 77.1000},
    'BOM': {'name': 'Chhatrapati Shivaji Maharaj International', 'city': 'Mumbai', 'country': 'India', 'region': 'asia', 'lat': 19.0896, 'lon': 72.8656},
    'MAA': {'name': 'Chennai International', 'city': 'Chennai', 'country': 'India', 'region': 'asia', 'lat': 12.9900, 'lon': 80.1693},
    'HYD': {'name': 'Rajiv Gandhi International', 'city': 'Hyderabad', 'country': 'India', 'region': 'asia', 'lat': 17.2313, 'lon': 78.4298},
    'BLR': {'name': 'Kempegowda International', 'city': 'Bengaluru', 'country': 'India', 'region': 'asia', 'lat': 13.1986, 'lon': 77.7066},
    'CCU': {'name': 'Netaji Subhas Chandra Bose International', 'city': 'Kolkata', 'country': 'India', 'region': 'asia', 'lat': 22.6520, 'lon': 88.4463},
    'COK': {'name': 'Cochin International', 'city': 'Kochi', 'country': 'India', 'region': 'asia', 'lat': 10.1520, 'lon': 76.4019},
    'DAC': {'name': 'Hazrat Shahjalal International', 'city': 'Dhaka', 'country': 'Bangladesh', 'region': 'asia', 'lat': 23.8433, 'lon': 90.3978},
    'CMB': {'name': 'Bandaranaike International', 'city': 'Colombo', 'country': 'Sri Lanka', 'region': 'asia', 'lat': 7.1808, 'lon': 79.8841},
    'KHI': {'name': 'Jinnah International', 'city': 'Karachi', 'country': 'Pakistan', 'region': 'asia', 'lat': 24.9065, 'lon': 67.1609},
    'LHE': {'name': 'Allama Iqbal International', 'city': 'Lahore', 'country': 'Pakistan', 'region': 'asia', 'lat': 31.5216, 'lon': 74.4036},
    'KTM': {'name': 'Tribhuvan International', 'city': 'Kathmandu', 'country': 'Nepal', 'region': 'asia', 'lat': 27.6966, 'lon': 85.3591},
    'RGN': {'name': 'Yangon International', 'city': 'Yangon', 'country': 'Myanmar', 'region': 'asia', 'lat': 16.9073, 'lon': 96.1332},
    'SGN': {'name': 'Tan Son Nhat International', 'city': 'Ho Chi Minh City', 'country': 'Vietnam', 'region': 'asia', 'lat': 10.8188, 'lon': 106.6520},
    'HAN': {'name': 'Noi Bai International', 'city': 'Hanoi', 'country': 'Vietnam', 'region': 'asia', 'lat': 21.2212, 'lon': 105.8072},
    'MNL': {'name': 'Ninoy Aquino International', 'city': 'Manila', 'country': 'Philippines', 'region': 'asia', 'lat': 14.5086, 'lon': 121.0197},
    'TPE': {'name': 'Taiwan Taoyuan International', 'city': 'Taipei', 'country': 'Taiwan', 'region': 'asia', 'lat': 25.0777, 'lon': 121.2327},
    # ── Oceania ──
    'SYD': {'name': 'Sydney Kingsford Smith', 'city': 'Sydney', 'country': 'Australia', 'region': 'oceania', 'lat': -33.9461, 'lon': 151.1772},
    'MEL': {'name': 'Melbourne Airport', 'city': 'Melbourne', 'country': 'Australia', 'region': 'oceania', 'lat': -37.6733, 'lon': 144.8430},
    'BNE': {'name': 'Brisbane Airport', 'city': 'Brisbane', 'country': 'Australia', 'region': 'oceania', 'lat': -27.3842, 'lon': 153.1175},
    'PER': {'name': 'Perth Airport', 'city': 'Perth', 'country': 'Australia', 'region': 'oceania', 'lat': -31.9403, 'lon': 115.9669},
    'ADL': {'name': 'Adelaide Airport', 'city': 'Adelaide', 'country': 'Australia', 'region': 'oceania', 'lat': -34.9450, 'lon': 138.5306},
    'AKL': {'name': 'Auckland Airport', 'city': 'Auckland', 'country': 'New Zealand', 'region': 'oceania', 'lat': -37.0082, 'lon': 174.7917},
    'CHC': {'name': 'Christchurch Airport', 'city': 'Christchurch', 'country': 'New Zealand', 'region': 'oceania', 'lat': -43.4894, 'lon': 172.5320},
}

BASE_PRICES = {
    # ── Nigeria domestic ──
    ('LOS', 'ABV'): (80, 150),
    ('LOS', 'PHC'): (90, 180),
    ('LOS', 'KAN'): (100, 200),
    ('LOS', 'ENU'): (85, 170),
    ('ABV', 'PHC'): (70, 140),
    ('ABV', 'KAN'): (75, 150),
    # ── West Africa ──
    ('LOS', 'ACC'): (200, 450),
    ('LOS', 'ABJ'): (210, 460),
    ('LOS', 'LFW'): (190, 420),
    ('LOS', 'COO'): (185, 400),
    ('LOS', 'DKR'): (280, 580),
    ('LOS', 'OUA'): (260, 520),
    ('LOS', 'BKO'): (270, 540),
    ('LOS', 'CKY'): (250, 500),
    ('LOS', 'DLA'): (230, 480),
    ('ABV', 'ACC'): (220, 480),
    ('ABV', 'DKR'): (300, 600),
    ('ACC', 'DKR'): (180, 360),
    ('ACC', 'ABJ'): (150, 300),
    # ── Africa to East/Southern Africa ──
    ('LOS', 'NBO'): (350, 700),
    ('LOS', 'ADD'): (380, 750),
    ('LOS', 'JNB'): (400, 800),
    ('LOS', 'KGL'): (360, 720),
    ('LOS', 'EBB'): (370, 730),
    ('LOS', 'DAR'): (390, 780),
    ('LOS', 'CPT'): (430, 860),
    ('LOS', 'MRU'): (480, 960),
    ('ABV', 'NBO'): (340, 680),
    ('ABV', 'JNB'): (390, 780),
    ('NBO', 'ADD'): (150, 300),
    ('NBO', 'JNB'): (250, 500),
    ('NBO', 'DAR'): (130, 260),
    ('NBO', 'KGL'): (120, 240),
    ('NBO', 'EBB'): (110, 220),
    ('NBO', 'CPT'): (300, 600),
    ('NBO', 'MRU'): (350, 700),
    ('ADD', 'JNB'): (300, 600),
    ('JNB', 'CPT'): (80, 200),
    ('JNB', 'MRU'): (250, 500),
    ('KGL', 'EBB'): (90, 180),
    ('KGL', 'DAR'): (140, 280),
    # ── North Africa ──
    ('LOS', 'CMN'): (300, 600),
    ('LOS', 'CAI'): (350, 700),
    ('LOS', 'TUN'): (330, 660),
    ('LOS', 'ALG'): (320, 640),
    ('ABV', 'CMN'): (290, 580),
    ('ABV', 'CAI'): (340, 680),
    ('NBO', 'CAI'): (280, 560),
    ('ADD', 'CAI'): (240, 480),
    ('JNB', 'CAI'): (350, 700),
    ('CMN', 'CAI'): (200, 400),
    ('CAI', 'TUN'): (180, 360),
    ('CAI', 'ALG'): (190, 380),
    # ── Africa to Middle East ──
    ('LOS', 'DXB'): (450, 900),
    ('LOS', 'DOH'): (470, 950),
    ('LOS', 'AUH'): (460, 920),
    ('LOS', 'JED'): (480, 960),
    ('LOS', 'RUH'): (490, 980),
    ('LOS', 'IST'): (480, 960),
    ('ABV', 'DXB'): (430, 880),
    ('ABV', 'DOH'): (440, 890),
    ('ABV', 'IST'): (460, 920),
    ('ACC', 'DXB'): (440, 880),
    ('NBO', 'DXB'): (350, 700),
    ('NBO', 'DOH'): (360, 720),
    ('NBO', 'IST'): (400, 800),
    ('ADD', 'DXB'): (320, 640),
    ('JNB', 'DXB'): (450, 900),
    ('CAI', 'DXB'): (250, 500),
    ('CAI', 'IST'): (220, 440),
    ('CMN', 'DXB'): (350, 700),
    # ── Africa to Europe ──
    ('LOS', 'LHR'): (550, 1100),
    ('LOS', 'CDG'): (580, 1150),
    ('LOS', 'AMS'): (560, 1120),
    ('LOS', 'FRA'): (570, 1130),
    ('LOS', 'MUC'): (575, 1140),
    ('LOS', 'DUS'): (565, 1125),
    ('LOS', 'BER'): (580, 1150),
    ('LOS', 'HAM'): (570, 1135),
    ('LOS', 'ZRH'): (590, 1160),
    ('LOS', 'BRU'): (560, 1110),
    ('LOS', 'MAD'): (540, 1080),
    ('LOS', 'BCN'): (550, 1100),
    ('LOS', 'FCO'): (520, 1040),
    ('LOS', 'ATH'): (530, 1060),
    ('LOS', 'VIE'): (575, 1140),
    ('LOS', 'LIS'): (510, 1020),
    ('ABV', 'LHR'): (530, 1080),
    ('ABV', 'CDG'): (550, 1100),
    ('ABV', 'FRA'): (545, 1090),
    ('ABV', 'AMS'): (535, 1070),
    ('ABV', 'MUC'): (548, 1095),
    ('ABV', 'DUS'): (538, 1075),
    ('ABV', 'ZRH'): (560, 1110),
    ('ABV', 'IST'): (460, 920),
    ('ACC', 'LHR'): (540, 1080),
    ('ACC', 'CDG'): (520, 1040),
    ('ACC', 'AMS'): (530, 1060),
    ('ACC', 'FRA'): (535, 1070),
    ('NBO', 'LHR'): (560, 1120),
    ('NBO', 'CDG'): (580, 1160),
    ('NBO', 'FRA'): (575, 1150),
    ('NBO', 'AMS'): (565, 1130),
    ('JNB', 'LHR'): (600, 1200),
    ('JNB', 'FRA'): (620, 1240),
    ('JNB', 'AMS'): (610, 1220),
    ('JNB', 'CDG'): (625, 1250),
    ('CMN', 'LHR'): (200, 450),
    ('CMN', 'CDG'): (180, 400),
    ('CMN', 'FRA'): (210, 460),
    ('CMN', 'MAD'): (150, 350),
    ('CAI', 'LHR'): (280, 560),
    ('CAI', 'FRA'): (270, 540),
    ('CAI', 'CDG'): (280, 560),
    ('TUN', 'FRA'): (160, 360),
    ('TUN', 'CDG'): (150, 340),
    ('ALG', 'CDG'): (170, 380),
    ('ALG', 'MAD'): (160, 360),
    # ── Africa to Americas ──
    ('LOS', 'JFK'): (750, 1500),
    ('LOS', 'IAD'): (720, 1450),
    ('LOS', 'ATL'): (740, 1480),
    ('LOS', 'ORD'): (760, 1520),
    ('LOS', 'MIA'): (730, 1460),
    ('LOS', 'YYZ'): (780, 1560),
    ('ABV', 'JFK'): (730, 1460),
    ('JNB', 'JFK'): (800, 1600),
    ('JNB', 'ATL'): (780, 1560),
    # ── Africa to Asia ──
    ('LOS', 'SIN'): (650, 1300),
    ('LOS', 'BKK'): (620, 1240),
    ('LOS', 'DEL'): (560, 1120),
    ('LOS', 'BOM'): (550, 1100),
    ('NBO', 'SIN'): (500, 1000),
    ('NBO', 'BOM'): (420, 840),
    ('NBO', 'DEL'): (430, 860),
    ('ADD', 'SIN'): (480, 960),
    ('JNB', 'SIN'): (550, 1100),
    ('JNB', 'BOM'): (500, 1000),
    # ── Germany domestic ──
    ('FRA', 'MUC'): (60, 180),
    ('FRA', 'DUS'): (55, 170),
    ('FRA', 'BER'): (65, 190),
    ('FRA', 'HAM'): (70, 200),
    ('FRA', 'STR'): (55, 160),
    ('FRA', 'CGN'): (50, 155),
    ('MUC', 'DUS'): (70, 200),
    ('MUC', 'BER'): (65, 185),
    ('MUC', 'HAM'): (75, 210),
    ('DUS', 'BER'): (60, 175),
    ('DUS', 'HAM'): (55, 165),
    ('BER', 'HAM'): (50, 150),
    # ── Intra-European ──
    ('FRA', 'LHR'): (100, 280),
    ('FRA', 'CDG'): (90, 250),
    ('FRA', 'AMS'): (85, 230),
    ('FRA', 'ZRH'): (80, 210),
    ('FRA', 'VIE'): (90, 240),
    ('FRA', 'BCN'): (110, 300),
    ('FRA', 'MAD'): (115, 310),
    ('FRA', 'FCO'): (110, 290),
    ('FRA', 'ATH'): (130, 350),
    ('FRA', 'IST'): (120, 330),
    ('FRA', 'CPH'): (100, 270),
    ('FRA', 'ARN'): (110, 290),
    ('FRA', 'OSL'): (105, 280),
    ('FRA', 'HEL'): (120, 310),
    ('FRA', 'WAW'): (100, 260),
    ('FRA', 'PRG'): (85, 225),
    ('FRA', 'BUD'): (95, 250),
    ('FRA', 'LIS'): (120, 320),
    ('FRA', 'OPO'): (115, 310),
    ('MUC', 'LHR'): (105, 285),
    ('MUC', 'CDG'): (95, 255),
    ('MUC', 'AMS'): (100, 270),
    ('MUC', 'ZRH'): (75, 200),
    ('MUC', 'VIE'): (80, 210),
    ('MUC', 'FCO'): (100, 270),
    ('MUC', 'BCN'): (115, 310),
    ('MUC', 'ATH'): (125, 340),
    ('MUC', 'IST'): (115, 315),
    ('MUC', 'CPH'): (105, 280),
    ('MUC', 'WAW'): (100, 260),
    ('MUC', 'PRG'): (80, 210),
    ('MUC', 'BUD'): (90, 240),
    ('DUS', 'LHR'): (95, 260),
    ('DUS', 'CDG'): (90, 245),
    ('DUS', 'AMS'): (70, 200),
    ('DUS', 'BCN'): (110, 295),
    ('DUS', 'MAD'): (115, 305),
    ('DUS', 'FCO'): (115, 305),
    ('DUS', 'ATH'): (130, 345),
    ('DUS', 'IST'): (120, 325),
    ('DUS', 'CPH'): (95, 255),
    ('DUS', 'ARN'): (100, 270),
    ('DUS', 'OSL'): (100, 265),
    ('DUS', 'WAW'): (100, 265),
    ('DUS', 'VIE'): (100, 265),
    ('DUS', 'ZRH'): (85, 230),
    ('DUS', 'LIS'): (115, 310),
    ('BER', 'LHR'): (100, 270),
    ('BER', 'CDG'): (100, 265),
    ('BER', 'AMS'): (90, 245),
    ('BER', 'BCN'): (115, 305),
    ('BER', 'MAD'): (120, 315),
    ('BER', 'ATH'): (130, 345),
    ('BER', 'IST'): (120, 325),
    ('BER', 'CPH'): (80, 220),
    ('BER', 'ARN'): (90, 240),
    ('BER', 'WAW'): (80, 215),
    ('BER', 'PRG'): (75, 205),
    ('BER', 'VIE'): (90, 240),
    ('LHR', 'CDG'): (80, 240),
    ('LHR', 'AMS'): (80, 235),
    ('LHR', 'BCN'): (100, 270),
    ('LHR', 'MAD'): (100, 275),
    ('LHR', 'FCO'): (110, 290),
    ('LHR', 'ATH'): (120, 330),
    ('LHR', 'IST'): (115, 315),
    ('LHR', 'CPH'): (90, 250),
    ('LHR', 'ARN'): (95, 260),
    ('LHR', 'OSL'): (90, 255),
    ('LHR', 'HEL'): (100, 270),
    ('LHR', 'VIE'): (110, 290),
    ('LHR', 'ZRH'): (100, 270),
    ('LHR', 'LIS'): (100, 270),
    ('AMS', 'BCN'): (105, 280),
    ('AMS', 'MAD'): (110, 290),
    ('AMS', 'FCO'): (115, 300),
    ('AMS', 'ATH'): (125, 330),
    ('AMS', 'IST'): (120, 320),
    ('AMS', 'CPH'): (85, 235),
    ('CDG', 'MAD'): (100, 270),
    ('CDG', 'BCN'): (95, 260),
    ('CDG', 'FCO'): (110, 285),
    ('CDG', 'ATH'): (120, 325),
    ('CDG', 'IST'): (115, 310),
    ('MAD', 'BCN'): (65, 180),
    ('MAD', 'FCO'): (110, 285),
    ('MAD', 'LIS'): (80, 215),
    ('MAD', 'ATH'): (120, 320),
    ('BCN', 'FCO'): (100, 265),
    ('BCN', 'ATH'): (115, 310),
    ('FCO', 'ATH'): (100, 270),
    ('ATH', 'IST'): (90, 240),
    ('ATH', 'CPH'): (120, 320),
    ('VIE', 'ATH'): (100, 270),
    ('VIE', 'IST'): (105, 280),
    ('VIE', 'ZRH'): (80, 215),
    ('VIE', 'WAW'): (85, 225),
    ('VIE', 'BUD'): (65, 175),
    ('VIE', 'PRG'): (70, 185),
    ('ZRH', 'BCN'): (105, 275),
    ('ZRH', 'FCO'): (90, 240),
    ('ZRH', 'LHR'): (95, 255),
    ('ZRH', 'CDG'): (85, 225),
    ('CPH', 'ARN'): (70, 190),
    ('CPH', 'OSL'): (65, 180),
    ('CPH', 'HEL'): (80, 215),
    ('ARN', 'OSL'): (60, 170),
    ('ARN', 'HEL'): (75, 200),
    ('WAW', 'BUD'): (90, 240),
    ('WAW', 'PRG'): (85, 230),
    ('PRG', 'BUD'): (80, 215),
    # ── Germany/Europe to Middle East ──
    ('FRA', 'DXB'): (350, 750),
    ('FRA', 'DOH'): (360, 760),
    ('FRA', 'AUH'): (355, 755),
    ('FRA', 'IST'): (120, 330),
    ('MUC', 'DXB'): (340, 730),
    ('MUC', 'DOH'): (350, 745),
    ('MUC', 'AUH'): (345, 735),
    ('DUS', 'DXB'): (345, 740),
    ('DUS', 'DOH'): (355, 750),
    ('DUS', 'AUH'): (348, 742),
    ('BER', 'DXB'): (350, 748),
    ('BER', 'DOH'): (358, 755),
    ('LHR', 'DXB'): (340, 720),
    ('LHR', 'DOH'): (350, 730),
    ('AMS', 'DXB'): (345, 725),
    ('CDG', 'DXB'): (350, 730),
    # ── Germany/Europe to Americas ──
    ('FRA', 'JFK'): (450, 1100),
    ('FRA', 'ORD'): (470, 1130),
    ('FRA', 'LAX'): (500, 1200),
    ('FRA', 'MIA'): (460, 1110),
    ('FRA', 'YYZ'): (480, 1140),
    ('FRA', 'YVR'): (510, 1220),
    ('FRA', 'GRU'): (550, 1300),
    ('FRA', 'EZE'): (580, 1350),
    ('MUC', 'JFK'): (445, 1090),
    ('MUC', 'ORD'): (465, 1125),
    ('MUC', 'LAX'): (495, 1195),
    ('MUC', 'YYZ'): (475, 1135),
    ('DUS', 'JFK'): (450, 1095),
    ('DUS', 'ORD'): (468, 1128),
    ('DUS', 'LAX'): (498, 1198),
    ('DUS', 'MIA'): (462, 1112),
    ('DUS', 'YYZ'): (478, 1138),
    ('BER', 'JFK'): (452, 1098),
    ('BER', 'LAX'): (500, 1200),
    ('LHR', 'JFK'): (430, 1050),
    ('LHR', 'LAX'): (490, 1170),
    ('LHR', 'ORD'): (450, 1080),
    ('LHR', 'YYZ'): (460, 1100),
    ('LHR', 'MIA'): (445, 1065),
    ('LHR', 'GRU'): (560, 1320),
    ('CDG', 'JFK'): (440, 1060),
    ('CDG', 'MIA'): (450, 1080),
    ('CDG', 'LAX'): (495, 1180),
    ('AMS', 'JFK'): (445, 1065),
    ('AMS', 'LAX'): (495, 1185),
    # ── Germany/Europe to Asia ──
    ('FRA', 'SIN'): (550, 1200),
    ('FRA', 'BKK'): (520, 1140),
    ('FRA', 'KUL'): (530, 1160),
    ('FRA', 'HKG'): (540, 1180),
    ('FRA', 'PVG'): (550, 1200),
    ('FRA', 'PEK'): (545, 1195),
    ('FRA', 'ICN'): (555, 1210),
    ('FRA', 'NRT'): (560, 1220),
    ('FRA', 'DEL'): (450, 1000),
    ('FRA', 'BOM'): (460, 1010),
    ('MUC', 'SIN'): (545, 1195),
    ('MUC', 'BKK'): (515, 1135),
    ('MUC', 'HKG'): (535, 1175),
    ('MUC', 'NRT'): (555, 1215),
    ('MUC', 'DEL'): (445, 995),
    ('MUC', 'BOM'): (455, 1005),
    ('DUS', 'SIN'): (548, 1198),
    ('DUS', 'BKK'): (518, 1138),
    ('DUS', 'HKG'): (538, 1178),
    ('DUS', 'DEL'): (448, 998),
    ('DUS', 'BOM'): (458, 1008),
    ('BER', 'SIN'): (550, 1200),
    ('BER', 'BKK'): (520, 1140),
    ('BER', 'DEL'): (450, 1000),
    ('LHR', 'SIN'): (530, 1150),
    ('LHR', 'BKK'): (500, 1100),
    ('LHR', 'HKG'): (520, 1130),
    ('LHR', 'NRT'): (540, 1170),
    ('LHR', 'DEL'): (430, 980),
    ('LHR', 'BOM'): (440, 990),
    ('AMS', 'SIN'): (535, 1155),
    ('AMS', 'BKK'): (505, 1105),
    ('AMS', 'DEL'): (435, 985),
    ('CDG', 'SIN'): (540, 1160),
    ('CDG', 'BKK'): (510, 1110),
    ('CDG', 'DEL'): (440, 990),
    # ── Germany/Europe to Africa ──
    ('FRA', 'LOS'): (570, 1130),
    ('FRA', 'ABV'): (545, 1090),
    ('FRA', 'ACC'): (535, 1070),
    ('FRA', 'NBO'): (575, 1150),
    ('FRA', 'JNB'): (620, 1240),
    ('FRA', 'CMN'): (210, 460),
    ('FRA', 'CAI'): (270, 540),
    ('FRA', 'ADD'): (560, 1120),
    ('MUC', 'LOS'): (575, 1140),
    ('MUC', 'NBO'): (570, 1140),
    ('MUC', 'JNB'): (615, 1235),
    ('MUC', 'CAI'): (265, 530),
    ('MUC', 'CMN'): (205, 450),
    ('DUS', 'LOS'): (565, 1125),
    ('DUS', 'ABV'): (540, 1080),
    ('DUS', 'ACC'): (530, 1065),
    ('DUS', 'NBO'): (568, 1138),
    ('DUS', 'JNB'): (612, 1228),
    ('DUS', 'CMN'): (200, 440),
    ('DUS', 'CAI'): (265, 530),
    ('BER', 'LOS'): (578, 1148),
    ('BER', 'NBO'): (572, 1142),
    ('BER', 'CMN'): (208, 452),
    ('BER', 'CAI'): (268, 535),
    ('LHR', 'LOS'): (550, 1100),
    ('LHR', 'NBO'): (560, 1120),
    ('LHR', 'JNB'): (600, 1200),
    ('LHR', 'CAI'): (280, 560),
    ('LHR', 'CMN'): (200, 450),
    ('AMS', 'LOS'): (560, 1120),
    ('AMS', 'NBO'): (565, 1130),
    ('AMS', 'JNB'): (610, 1220),
    ('AMS', 'CMN'): (205, 455),
    ('CDG', 'LOS'): (580, 1150),
    ('CDG', 'NBO'): (580, 1160),
    ('CDG', 'CMN'): (180, 400),
    ('CDG', 'CAI'): (280, 560),
    # ── Americas domestic/regional ──
    ('JFK', 'LAX'): (150, 400),
    ('JFK', 'ORD'): (100, 280),
    ('JFK', 'ATL'): (100, 270),
    ('JFK', 'MIA'): (100, 275),
    ('JFK', 'BOS'): (70, 200),
    ('JFK', 'DFW'): (130, 350),
    ('JFK', 'SEA'): (160, 420),
    ('JFK', 'SFO'): (165, 430),
    ('JFK', 'DEN'): (140, 380),
    ('JFK', 'YYZ'): (100, 280),
    ('JFK', 'YUL'): (90, 260),
    ('JFK', 'MEX'): (200, 500),
    ('JFK', 'GRU'): (550, 1200),
    ('JFK', 'EZE'): (600, 1300),
    ('JFK', 'BOG'): (350, 750),
    ('LAX', 'SFO'): (60, 180),
    ('LAX', 'SEA'): (100, 260),
    ('LAX', 'DEN'): (110, 290),
    ('LAX', 'YVR'): (110, 295),
    ('LAX', 'MEX'): (180, 450),
    ('ORD', 'ATL'): (100, 270),
    ('ORD', 'MIA'): (130, 340),
    ('ORD', 'DFW'): (110, 290),
    ('ATL', 'MIA'): (80, 220),
    ('ATL', 'YYZ'): (130, 340),
    ('MIA', 'MEX'): (200, 480),
    ('MIA', 'GRU'): (480, 1050),
    ('MIA', 'BOG'): (280, 620),
    ('MIA', 'LIM'): (380, 820),
    ('YYZ', 'YVR'): (150, 380),
    ('YYZ', 'YUL'): (80, 220),
    ('GRU', 'EZE'): (150, 380),
    ('GRU', 'SCL'): (200, 480),
    ('GRU', 'BOG'): (280, 620),
    ('EZE', 'SCL'): (120, 300),
    ('EZE', 'LIM'): (200, 480),
    ('BOG', 'LIM'): (200, 480),
    ('BOG', 'PTY'): (150, 380),
    ('MEX', 'BOG'): (280, 620),
    # ── Americas to Asia/Oceania ──
    ('JFK', 'NRT'): (600, 1300),
    ('JFK', 'ICN'): (580, 1260),
    ('JFK', 'HKG'): (620, 1340),
    ('JFK', 'SIN'): (680, 1450),
    ('LAX', 'NRT'): (500, 1100),
    ('LAX', 'ICN'): (480, 1060),
    ('LAX', 'HKG'): (520, 1140),
    ('LAX', 'SIN'): (560, 1220),
    ('LAX', 'SYD'): (600, 1300),
    ('LAX', 'MEL'): (610, 1320),
    ('LAX', 'AKL'): (580, 1260),
    ('JFK', 'SYD'): (750, 1600),
    # ── Asia intra ──
    ('SIN', 'BKK'): (120, 300),
    ('SIN', 'KUL'): (80, 220),
    ('SIN', 'CGK'): (110, 280),
    ('SIN', 'HKG'): (150, 380),
    ('SIN', 'PVG'): (200, 480),
    ('SIN', 'ICN'): (250, 580),
    ('SIN', 'NRT'): (280, 640),
    ('SIN', 'DEL'): (280, 620),
    ('SIN', 'BOM'): (290, 640),
    ('SIN', 'CMB'): (180, 420),
    ('SIN', 'SYD'): (350, 780),
    ('SIN', 'MEL'): (360, 800),
    ('BKK', 'KUL'): (100, 260),
    ('BKK', 'HKG'): (160, 400),
    ('BKK', 'DEL'): (220, 520),
    ('BKK', 'NRT'): (280, 640),
    ('HKG', 'PVG'): (120, 300),
    ('HKG', 'ICN'): (160, 380),
    ('HKG', 'NRT'): (200, 460),
    ('HKG', 'SYD'): (380, 840),
    ('PVG', 'ICN'): (120, 280),
    ('PVG', 'NRT'): (150, 360),
    ('ICN', 'NRT'): (100, 260),
    ('DEL', 'BOM'): (70, 190),
    ('DEL', 'MAA'): (80, 200),
    ('DEL', 'BLR'): (85, 210),
    ('DEL', 'HYD'): (80, 200),
    ('DEL', 'CCU'): (75, 190),
    ('DEL', 'DXB'): (180, 420),
    ('DEL', 'DOH'): (190, 430),
    ('BOM', 'DXB'): (160, 380),
    ('BOM', 'DOH'): (170, 400),
    ('BOM', 'SIN'): (290, 640),
    ('NRT', 'SYD'): (400, 900),
    ('NRT', 'MEL'): (410, 920),
    # ── Oceania ──
    ('SYD', 'MEL'): (60, 180),
    ('SYD', 'BNE'): (70, 200),
    ('SYD', 'PER'): (150, 380),
    ('SYD', 'AKL'): (200, 480),
    ('MEL', 'BNE'): (70, 195),
    ('MEL', 'PER'): (145, 370),
    ('MEL', 'AKL'): (210, 490),
    ('BNE', 'AKL'): (180, 420),
}

# Airlines that actually serve specific airports.
# If an origin or destination is listed here, only these airlines appear in results.
# Major hubs (LOS, ABV, FRA, LHR, DXB, etc.) are NOT listed — they get the full pool.
AIRPORT_CARRIERS = {
    # Nigerian regional — Gulf/European/Asian majors do NOT fly here
    'PHC': {'Air Peace', 'Arik Air', 'IbomAir', 'Ethiopian Airlines', 'Kenya Airways', 'RwandAir'},
    'KAN': {'Air Peace', 'Arik Air', 'IbomAir', 'Ethiopian Airlines', 'RwandAir'},
    'ENU': {'Air Peace', 'Arik Air', 'IbomAir'},
    # West Africa regional
    'DLA': {"Air Côte d'Ivoire", 'ASKY Airlines', 'Ethiopian Airlines', 'Royal Air Maroc', 'Air France'},
    'LFW': {'ASKY Airlines', 'Ethiopian Airlines', 'Royal Air Maroc', 'Air France', "Air Côte d'Ivoire"},
    'COO': {'ASKY Airlines', 'Ethiopian Airlines', 'Royal Air Maroc', 'Air France', "Air Côte d'Ivoire"},
    'OUA': {"Air Côte d'Ivoire", 'ASKY Airlines', 'Ethiopian Airlines', 'Royal Air Maroc', 'Air France', 'Turkish Airlines'},
    'BKO': {'Air France', 'Royal Air Maroc', 'Turkish Airlines', "Air Côte d'Ivoire", 'ASKY Airlines', 'Ethiopian Airlines'},
    'CKY': {'Air France', 'Royal Air Maroc', "Air Côte d'Ivoire", 'ASKY Airlines', 'Ethiopian Airlines'},
    # East Africa specific
    'JRO': {'Ethiopian Airlines', 'Kenya Airways', 'RwandAir', 'KLM'},
    'EBB': {'Ethiopian Airlines', 'Kenya Airways', 'RwandAir', 'Emirates', 'Qatar Airways', 'Turkish Airlines'},
    # Southern Africa regional
    'MPM': {'South African Airways', 'Ethiopian Airlines', 'Kenya Airways', 'RwandAir', 'Emirates'},
    # German secondary airports — only short/medium haul carriers serve these
    'STR': {'Lufthansa', 'Eurowings', 'Ryanair', 'EasyJet', 'Turkish Airlines', 'Wizz Air'},
    'CGN': {'Eurowings', 'Ryanair', 'EasyJet', 'Wizz Air', 'Turkish Airlines'},
    'NUE': {'Lufthansa', 'Eurowings', 'Ryanair', 'EasyJet'},
    'HAJ': {'Lufthansa', 'Eurowings', 'Ryanair', 'EasyJet', 'Wizz Air'},
    'LEJ': {'Ryanair', 'EasyJet', 'Wizz Air', 'Eurowings'},
    'DRS': {'Ryanair', 'EasyJet', 'Eurowings', 'Lufthansa'},
    'FKB': {'Ryanair', 'EasyJet', 'Wizz Air'},
    # UK regional
    'EDI': {'British Airways', 'EasyJet', 'Ryanair', 'Eurowings', 'KLM', 'Lufthansa'},
    'BHX': {'British Airways', 'Ryanair', 'EasyJet', 'Wizz Air', 'Turkish Airlines', 'KLM'},
    'GLA': {'British Airways', 'EasyJet', 'Ryanair', 'KLM'},
    'MAN': {'British Airways', 'EasyJet', 'Ryanair', 'Jet2', 'Emirates', 'Qatar Airways', 'Turkish Airlines', 'KLM', 'Lufthansa'},
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

    # Generate 3-6 flight options using only plausible airlines for this route
    o_region = AIRPORTS.get(origin, {}).get('region', '')
    d_region = AIRPORTS.get(destination, {}).get('region', '')
    pool = _eligible_airlines(o_region, d_region)
    pool = _apply_airport_restrictions(pool, origin, destination)
    num_results = random.randint(3, 6)
    used_airlines = random.sample(pool, min(num_results, len(pool)))

    for i, airline in enumerate(used_airlines):
        base = round(random.uniform(price_range[0], price_range[1]) * cabin_mult, 2)
        stops_info = random.choice(STOPS) if i > 0 else STOPS[0]  # First result is nonstop

        dep_hour = random.randint(5, 22)
        dep_min = random.choice([0, 15, 30, 45])
        duration_hrs = _estimate_duration(origin, destination, stops_info['stops'])
        arr_hour = int((dep_hour + duration_hrs) % 24)

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

@lru_cache(maxsize=512)
def _estimate_duration(origin, destination, stops):
    orig = AIRPORTS.get(origin, {})
    dest = AIRPORTS.get(destination, {})
    if 'lat' in orig and 'lat' in dest:
        dist_km = _haversine_km(orig['lat'], orig['lon'], dest['lat'], dest['lon'])
        base = round(1.0 + dist_km / 870, 1)
    else:
        base = 4.0
    return base + stops * 2

_FEATURED_ROUTE_DEFS = [
    {'origin': 'LOS', 'destination': 'LHR', 'label': 'Lagos → London'},
    {'origin': 'LOS', 'destination': 'DXB', 'label': 'Lagos → Dubai'},
    {'origin': 'ABV', 'destination': 'NBO', 'label': 'Abuja → Nairobi'},
    {'origin': 'LOS', 'destination': 'JFK', 'label': 'Lagos → New York'},
    {'origin': 'ACC', 'destination': 'ADD', 'label': 'Accra → Addis Ababa'},
    {'origin': 'NBO', 'destination': 'JNB', 'label': 'Nairobi → Johannesburg'},
]

_featured_cache = {'data': None, 'ts': 0}
_FEATURED_TTL = 300  # 5 minutes


def get_featured_routes(force_refresh=False):
    now = time.time()
    if not force_refresh and _featured_cache['data'] and (now - _featured_cache['ts']) < _FEATURED_TTL:
        return _featured_cache['data']

    search_date = (datetime.now() + timedelta(days=14)).strftime('%Y-%m-%d')
    results = []
    for route in _FEATURED_ROUTE_DEFS:
        try:
            flights = search_flights(route['origin'], route['destination'], search_date)
            if not flights:
                continue
            cheapest = min(flights, key=lambda f: f['pricing']['total'])
            results.append({
                'origin': route['origin'],
                'destination': route['destination'],
                'label': route['label'],
                'airline': cheapest['airline'],
                'price_from': cheapest['pricing']['total'],
                'departure_time': cheapest['departure_time'],
                'duration_hours': cheapest['duration_hours'],
                'stops': cheapest['stops'],
                'stops_label': cheapest['stops_label'],
            })
        except Exception:
            continue

    fetched_at = datetime.utcnow().strftime('%H:%M UTC')
    payload = {'routes': results, 'fetched_at': fetched_at, 'search_date': search_date}
    _featured_cache['data'] = payload
    _featured_cache['ts'] = now
    return payload

def get_airports():
    return [{'code': k, **v} for k, v in AIRPORTS.items()]
