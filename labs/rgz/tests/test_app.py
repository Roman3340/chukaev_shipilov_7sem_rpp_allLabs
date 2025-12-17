import json
import sys
import os
import uuid
from dotenv import load_dotenv

load_dotenv()

# sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
#
# from app import app
from ..app import app


def generate_unique_username():
    """Generate unique username"""
    return f"user_{uuid.uuid4().hex[:8]}"


def cleanup_test_user(username):
    """Cleanup test user from DB"""
    try:
        import psycopg2
        conn = psycopg2.connect(
            host='localhost',
            database='subscriptions_db',
            user='flask_user',
            password=os.getenv('rgz_db_password', 'password')
        )
        cur = conn.cursor()

        cur.execute("DELETE FROM audit_log WHERE user_id IN (SELECT id FROM users WHERE username = %s)", (username,))
        cur.execute("DELETE FROM subscriptions WHERE user_id IN (SELECT id FROM users WHERE username = %s)",
                    (username,))
        cur.execute("DELETE FROM users WHERE username = %s", (username,))

        conn.commit()
        cur.close()
        conn.close()
    except Exception:
        pass



def test_register_and_login():
    """Test 1: Registration and login"""
    username = generate_unique_username()

    app.config['TESTING'] = True
    client = app.test_client()

    try:
        response = client.post('/api/register',
                               json={'username': username, 'password': 'testpass'})
        assert response.status_code == 201
        data = json.loads(response.data)
        user_id = data['user_id']

        response = client.post('/api/login',
                               json={'username': username, 'password': 'testpass'})
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['message'] == 'Login successful'
        assert data['user_id'] == user_id

    finally:
        cleanup_test_user(username)


def test_create_and_get_subscription():
    """Test 2: Create and get subscription"""
    username = generate_unique_username()

    app.config['TESTING'] = True
    client = app.test_client()

    try:
        response = client.post('/api/register',
                               json={'username': username, 'password': 'testpass'})
        user_data = json.loads(response.data)
        user_id = user_data['user_id']

        response = client.post('/api/subscriptions',
                               json={
                                   'user_id': user_id,
                                   'name': 'Netflix',
                                   'amount': 599,
                                   'periodicity': 'monthly',
                                   'start_date': '2024-01-01'
                               })
        assert response.status_code == 201

        response = client.get(f'/api/subscriptions?user_id={user_id}')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data['subscriptions']) == 1
        assert data['subscriptions'][0]['name'] == 'Netflix'

    finally:
        cleanup_test_user(username)


def test_update_subscription():
    """Test 3: Update subscription"""
    username = generate_unique_username()

    app.config['TESTING'] = True
    client = app.test_client()

    try:
        response = client.post('/api/register',
                               json={'username': username, 'password': 'testpass'})
        user_data = json.loads(response.data)
        user_id = user_data['user_id']

        response = client.post('/api/subscriptions',
                               json={
                                   'user_id': user_id,
                                   'name': 'Spotify',
                                   'amount': 199,
                                   'periodicity': 'monthly',
                                   'start_date': '2024-01-01'
                               })
        sub_data = json.loads(response.data)
        sub_id = sub_data['id']

        response = client.put(f'/api/subscriptions/{sub_id}',
                              json={'user_id': user_id, 'amount': 299})
        assert response.status_code == 200

    finally:
        cleanup_test_user(username)


def test_delete_subscription():
    """Test 4: Delete subscription"""
    username = generate_unique_username()

    app.config['TESTING'] = True
    client = app.test_client()

    try:
        response = client.post('/api/register',
                               json={'username': username, 'password': 'testpass'})
        user_data = json.loads(response.data)
        user_id = user_data['user_id']

        response = client.post('/api/subscriptions',
                               json={
                                   'user_id': user_id,
                                   'name': 'Yandex Plus',
                                   'amount': 299,
                                   'periodicity': 'monthly',
                                   'start_date': '2024-01-01'
                               })
        sub_data = json.loads(response.data)
        sub_id = sub_data['id']

        response = client.delete(f'/api/subscriptions/{sub_id}',
                                 json={'user_id': user_id})
        assert response.status_code == 200

        response = client.get(f'/api/subscriptions?user_id={user_id}')
        data = json.loads(response.data)
        assert len(data['subscriptions']) == 0

    finally:
        cleanup_test_user(username)
