def test_customer_register(client):
    resp = client.post('/api/auth/register', json={
        'email': 'test@example.com',
        'password': 'Test1234!',
        'first_name': 'Test',
        'last_name': 'User',
    })
    assert resp.status_code == 201
    data = resp.get_json()
    assert 'token' in data
    assert data['user']['email'] == 'test@example.com'

def test_duplicate_register(client):
    payload = {'email': 'dup@example.com', 'password': 'Test1234!', 'first_name': 'A', 'last_name': 'B'}
    client.post('/api/auth/register', json=payload)
    resp = client.post('/api/auth/register', json=payload)
    assert resp.status_code == 409

def test_customer_login(client):
    client.post('/api/auth/register', json={
        'email': 'login@example.com', 'password': 'Test1234!',
        'first_name': 'Login', 'last_name': 'User',
    })
    resp = client.post('/api/auth/login', json={'email': 'login@example.com', 'password': 'Test1234!'})
    assert resp.status_code == 200
    assert 'token' in resp.get_json()

def test_login_wrong_password(client):
    client.post('/api/auth/register', json={
        'email': 'wrong@example.com', 'password': 'Test1234!',
        'first_name': 'W', 'last_name': 'U',
    })
    resp = client.post('/api/auth/login', json={'email': 'wrong@example.com', 'password': 'wrongpass'})
    assert resp.status_code == 401

def test_staff_login(client):
    from backend.config import Config
    resp = client.post('/api/staff/auth/login', json={
        'email': Config.SUPER_ADMIN_EMAIL,
        'password': Config.SUPER_ADMIN_PASSWORD,
    })
    assert resp.status_code == 200
    data = resp.get_json()
    assert 'token' in data
    assert data['staff']['role'] == 'super_admin'

def test_forgot_password_always_200(client):
    resp = client.post('/api/auth/forgot-password', json={'email': 'nobody@example.com'})
    assert resp.status_code == 200
