from flask import Blueprint, request, jsonify
from backend.services.mock_flights import search_flights, get_featured_routes, get_airports
from backend.services.ai_search import parse_natural_language
from backend.services.pricing import calculate_total, BAGGAGE_FEES, SEAT_FEES

bp = Blueprint('flights', __name__, url_prefix='/api/flights')

@bp.route('/search', methods=['GET'])
def search():
    origin = request.args.get('origin', '').upper()
    destination = request.args.get('destination', '').upper()
    departure_date = request.args.get('departure_date')
    passengers = int(request.args.get('passengers', 1))
    cabin = request.args.get('cabin', 'economy')
    return_date = request.args.get('return_date')

    if not origin or not destination or not departure_date:
        return jsonify({'error': 'origin, destination, and departure_date are required'}), 400

    passengers = max(1, min(passengers, 9))
    results = search_flights(origin, destination, departure_date, passengers, cabin, return_date)

    # Apply budget filter if provided
    budget = request.args.get('budget_max')
    if budget:
        try:
            results = [f for f in results if f['pricing']['total'] <= float(budget)]
        except (ValueError, TypeError):
            pass

    return jsonify({
        'results': results,
        'count': len(results),
        'origin': origin,
        'destination': destination,
        'departure_date': departure_date,
        'passengers': passengers,
        'cabin': cabin,
    })

@bp.route('/search/ai', methods=['POST'])
def ai_search():
    data = request.get_json()
    query = data.get('query', '').strip()
    if not query:
        return jsonify({'error': 'query is required'}), 400

    parsed = parse_natural_language(query)

    if not parsed['origin'] or not parsed['destination']:
        return jsonify({
            'parsed': parsed,
            'results': [],
            'suggestion': 'Could not identify origin or destination. Try: "flight from Lagos to London next month"'
        })

    results = search_flights(
        parsed['origin'],
        parsed['destination'],
        parsed['departure_date'],
        parsed['passengers'],
        parsed['cabin'],
    )

    if parsed.get('budget_max_usd'):
        results = [r for r in results if r['pricing']['total'] <= parsed['budget_max_usd']]

    return jsonify({
        'parsed': parsed,
        'results': results,
        'count': len(results),
    })

@bp.route('/search/multicity', methods=['POST'])
def multicity_search():
    data = request.get_json()
    legs = data.get('legs', [])
    passengers = max(1, min(int(data.get('passengers', 1)), 9))
    cabin = data.get('cabin', 'economy')

    if len(legs) < 2:
        return jsonify({'error': 'At least 2 legs required'}), 400
    if len(legs) > 6:
        return jsonify({'error': 'Maximum 6 legs allowed'}), 400

    results = []
    for i, leg in enumerate(legs):
        origin = leg.get('origin', '').upper()
        destination = leg.get('destination', '').upper()
        date = leg.get('date', '')
        if not origin or not destination or not date:
            return jsonify({'error': f'Leg {i+1}: origin, destination, and date required'}), 400
        flights = search_flights(origin, destination, date, passengers, cabin)
        results.append({
            'leg_num': i + 1,
            'origin': origin,
            'destination': destination,
            'date': date,
            'flights': flights,
        })

    return jsonify({'legs': results, 'passengers': passengers, 'cabin': cabin})

@bp.route('/featured', methods=['GET'])
def featured():
    return jsonify(get_featured_routes())

@bp.route('/airports', methods=['GET'])
def airports():
    return jsonify(get_airports())

@bp.route('/pricing/calculate', methods=['POST'])
def calculate_price():
    data = request.get_json()
    base_fare = data.get('base_fare')
    if base_fare is None:
        return jsonify({'error': 'base_fare required'}), 400

    result = calculate_total(
        base_fare=float(base_fare),
        passengers=int(data.get('passengers', 1)),
        baggage_option=data.get('baggage', 'carry_on'),
        seat_option=data.get('seat', 'standard'),
    )
    return jsonify(result)

@bp.route('/pricing/options', methods=['GET'])
def pricing_options():
    return jsonify({
        'baggage': [{'id': k, 'label': k.replace('_', ' ').title(), 'fee_usd': v} for k, v in BAGGAGE_FEES.items()],
        'seats': [{'id': k, 'label': k.replace('_', ' ').title(), 'fee_usd': v} for k, v in SEAT_FEES.items()],
    })
