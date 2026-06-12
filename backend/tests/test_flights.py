def test_flight_search(client):
    resp = client.get('/api/flights/search?origin=LOS&destination=LHR&departure_date=2026-08-15')
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['count'] > 0
    first = data['results'][0]
    assert 'pricing' in first
    assert 'total' in first['pricing']
    assert 'ota_options' in first

def test_flight_search_missing_params(client):
    resp = client.get('/api/flights/search?origin=LOS')
    assert resp.status_code == 400

def test_ai_search(client):
    resp = client.post('/api/flights/search/ai', json={'query': 'cheap flight from Lagos to London next month'})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['parsed']['origin'] == 'LOS'
    assert data['parsed']['destination'] == 'LHR'

def test_featured_routes(client):
    resp = client.get('/api/flights/featured')
    assert resp.status_code == 200
    assert len(resp.get_json()) > 0

def test_airports(client):
    resp = client.get('/api/flights/airports')
    assert resp.status_code == 200
    airports = resp.get_json()
    codes = [a['code'] for a in airports]
    assert 'LOS' in codes
    assert 'LHR' in codes

def test_pricing_calculate(client):
    resp = client.post('/api/flights/pricing/calculate', json={
        'base_fare': 500, 'passengers': 2, 'baggage': 'checked_1', 'seat': 'window'
    })
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['total'] > 500 * 2  # Should include fees
