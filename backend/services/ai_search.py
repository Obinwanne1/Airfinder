import re

CITY_TO_IATA = {
    'lagos': 'LOS', 'abuja': 'ABV', 'port harcourt': 'PHC',
    'accra': 'ACC', 'nairobi': 'NBO', 'addis ababa': 'ADD',
    'johannesburg': 'JNB', 'joburg': 'JNB', 'jnb': 'JNB',
    'casablanca': 'CMN', 'kigali': 'KGL', 'dakar': 'DKR',
    'dubai': 'DXB', 'doha': 'DOH',
    'london': 'LHR', 'paris': 'CDG', 'amsterdam': 'AMS',
    'frankfurt': 'FRA', 'istanbul': 'IST',
    'new york': 'JFK', 'nyc': 'JFK', 'washington': 'IAD',
    'toronto': 'YYZ',
}

MONTH_MAP = {
    'january': '01', 'february': '02', 'march': '03', 'april': '04',
    'may': '05', 'june': '06', 'july': '07', 'august': '08',
    'september': '09', 'october': '10', 'november': '11', 'december': '12',
    'jan': '01', 'feb': '02', 'mar': '03', 'apr': '04',
    'jun': '06', 'jul': '07', 'aug': '08', 'sep': '09',
    'oct': '10', 'nov': '11', 'dec': '12',
}

CABIN_KEYWORDS = {
    'business': 'business', 'business class': 'business',
    'first class': 'first', 'first': 'first',
    'premium economy': 'premium_economy', 'premium': 'premium_economy',
    'economy': 'economy', 'cheap': 'economy', 'budget': 'economy',
}

def parse_natural_language(query: str) -> dict:
    q = query.lower().strip()
    result = {
        'origin': None,
        'destination': None,
        'departure_date': None,
        'return_date': None,
        'passengers': 1,
        'cabin': 'economy',
        'budget_max_usd': None,
        'raw_query': query,
    }

    # Extract IATA codes directly (e.g. LOS, LHR)
    iata_codes = re.findall(r'\b([A-Z]{3})\b', query.upper())

    # Extract city names
    cities_found = []
    for city, code in CITY_TO_IATA.items():
        if city in q:
            cities_found.append(code)

    # Merge and deduplicate preserving order
    all_codes = iata_codes + [c for c in cities_found if c not in iata_codes]

    # Route extraction via "to", "from", "→"
    to_match = re.search(r'(?:from\s+(\w[\w\s]+?)\s+to\s+(\w[\w\s]+?))\s', q + ' ')
    if to_match:
        src = _city_to_code(to_match.group(1).strip())
        dst = _city_to_code(to_match.group(2).strip())
        if src:
            result['origin'] = src
        if dst:
            result['destination'] = dst
    elif len(all_codes) >= 2:
        result['origin'] = all_codes[0]
        result['destination'] = all_codes[1]
    elif len(all_codes) == 1:
        result['destination'] = all_codes[0]

    # Date extraction
    from datetime import datetime, timedelta
    today = datetime.utcnow()

    if 'next month' in q:
        d = today.replace(day=1) + timedelta(days=32)
        result['departure_date'] = d.replace(day=15).strftime('%Y-%m-%d')
    elif 'this month' in q:
        result['departure_date'] = (today + timedelta(days=7)).strftime('%Y-%m-%d')
    else:
        for month_name, month_num in MONTH_MAP.items():
            if month_name in q:
                year = today.year if int(month_num) >= today.month else today.year + 1
                result['departure_date'] = f"{year}-{month_num}-15"
                break

    if not result['departure_date']:
        result['departure_date'] = (today + timedelta(days=14)).strftime('%Y-%m-%d')

    # Passengers
    pax_match = re.search(r'(\d+)\s*(?:passenger|people|person|adult|pax)', q)
    if pax_match:
        result['passengers'] = min(int(pax_match.group(1)), 9)

    # Cabin class
    for keyword, cabin in CABIN_KEYWORDS.items():
        if keyword in q:
            result['cabin'] = cabin
            break

    # Budget
    budget_match = re.search(r'(?:under|below|max|budget)\s*[\$£₦]?\s*([\d,]+)', q)
    if budget_match:
        amount = int(budget_match.group(1).replace(',', ''))
        # Naira to USD rough conversion
        if '₦' in query or 'naira' in q or amount > 100000:
            amount = round(amount / 1500)
        result['budget_max_usd'] = amount

    return result

def _city_to_code(name: str) -> str:
    name = name.strip().lower()
    return CITY_TO_IATA.get(name)
