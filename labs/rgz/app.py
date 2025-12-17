from flask import Flask, request, jsonify
import psycopg2
from werkzeug.security import generate_password_hash, check_password_hash
import os
from dotenv import load_dotenv


load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('flask_secret', 'secret-key')

# Подключение к базе данных
def get_db():
    conn = psycopg2.connect(
        host='localhost',
        database='subscriptions_db',
        user='flask_user',
        password=os.getenv('rgz_db_password', 'password')
    )
    return conn



# 1. Регистрация
@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No data provided'}), 400

    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400

    conn = get_db()
    cur = conn.cursor()

    # Проверяем, не занято ли имя
    cur.execute("SELECT id FROM users WHERE username = %s", (username,))
    if cur.fetchone():
        cur.close()
        conn.close()
        return jsonify({'error': 'Username already exists'}), 400

    # Создаем пользователя
    password_hash = generate_password_hash(password)
    cur.execute(
        "INSERT INTO users (username, password_hash) VALUES (%s, %s) RETURNING id",
        (username, password_hash)
    )

    user_id = cur.fetchone()[0]

    # Логируем в аудит
    cur.execute(
        "INSERT INTO audit_log (user_id, action) VALUES (%s, %s)",
        (user_id, 'REGISTER')
    )

    conn.commit()
    cur.close()
    conn.close()

    return jsonify({'message': 'User created successfully', 'user_id': user_id}), 201


@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()

    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400

    conn = get_db()
    cur = conn.cursor()

    # Получаем пользователя с хешем
    cur.execute("SELECT id, password_hash FROM users WHERE username = %s", (username,))
    user = cur.fetchone()
    cur.close()
    conn.close()

    if user:
        user_id = user[0]
        stored_hash = user[1]

        # Проверяем пароль
        if check_password_hash(stored_hash, password):
            return jsonify({'message': 'Login successful', 'user_id': user_id})

    return jsonify({'error': 'Invalid username or password'}), 401

# 3. Создание подписки
@app.route('/api/subscriptions', methods=['POST'])
def create_subscription():
    data = request.get_json()

    user_id = data.get('user_id')
    name = data.get('name')
    amount = data.get('amount')
    periodicity = data.get('periodicity')
    start_date = data.get('start_date')

    # Проверяем что все нужные поля есть
    if not all([user_id, name, amount, periodicity, start_date]):
        return jsonify({'error': 'All fields are required: user_id, name, amount, periodicity, start_date'}), 400

    conn = get_db()
    cur = conn.cursor()

    # Проверяем что пользователь существует
    cur.execute("SELECT id FROM users WHERE id = %s", (user_id,))
    if not cur.fetchone():
        cur.close()
        conn.close()
        return jsonify({'error': 'User not found'}), 404

    # Создаем подписку
    cur.execute(
        """INSERT INTO subscriptions (user_id, name, amount, periodicity, start_date) 
           VALUES (%s, %s, %s, %s, %s) RETURNING id""",
        (user_id, name, amount, periodicity, start_date)
    )

    sub_id = cur.fetchone()[0]

    # Логируем в аудит
    cur.execute(
        "INSERT INTO audit_log (user_id, action) VALUES (%s, %s)",
        (user_id, 'CREATE_SUBSCRIPTION')
    )

    conn.commit()
    cur.close()
    conn.close()

    return jsonify({'message': 'Subscription created', 'id': sub_id}), 201


# 4. Получить все подписки пользователя
@app.route('/api/subscriptions', methods=['GET'])
def get_subscriptions():
    user_id = request.args.get('user_id')

    if not user_id:
        return jsonify({'error': 'user_id parameter is required'}), 400

    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        "SELECT id, name, amount, periodicity, start_date FROM subscriptions WHERE user_id = %s",
        (user_id,)
    )

    subscriptions = []
    for row in cur.fetchall():
        subscriptions.append({
            'id': row[0],
            'name': row[1],
            'amount': row[2],
            'periodicity': row[3],
            'start_date': row[4]
        })

    cur.close()
    conn.close()

    return jsonify({'subscriptions': subscriptions})


# 5. Обновить подписку
@app.route('/api/subscriptions/<int:sub_id>', methods=['PUT'])
def update_subscription(sub_id):
    data = request.get_json()

    user_id = data.get('user_id')

    if not user_id:
        return jsonify({'error': 'user_id is required'}), 400

    conn = get_db()
    cur = conn.cursor()

    # Проверяем что подписка принадлежит пользователю
    cur.execute(
        "SELECT id FROM subscriptions WHERE id = %s AND user_id = %s",
        (sub_id, user_id)
    )

    if not cur.fetchone():
        cur.close()
        conn.close()
        return jsonify({'error': 'Subscription not found'}), 404

    # Обновляем поля
    if 'name' in data:
        cur.execute(
            "UPDATE subscriptions SET name = %s WHERE id = %s",
            (data['name'], sub_id)
        )

    if 'amount' in data:
        cur.execute(
            "UPDATE subscriptions SET amount = %s WHERE id = %s",
            (data['amount'], sub_id)
        )

    if 'periodicity' in data:
        cur.execute(
            "UPDATE subscriptions SET periodicity = %s WHERE id = %s",
            (data['periodicity'], sub_id)
        )

    if 'start_date' in data:
        cur.execute(
            "UPDATE subscriptions SET start_date = %s WHERE id = %s",
            (data['start_date'], sub_id)
        )

    # Логируем в аудит
    cur.execute(
        "INSERT INTO audit_log (user_id, action) VALUES (%s, %s)",
        (user_id, 'UPDATE_SUBSCRIPTION')
    )

    conn.commit()
    cur.close()
    conn.close()

    return jsonify({'message': 'Subscription updated successfully'})


# 6. Удалить подписку
@app.route('/api/subscriptions/<int:sub_id>', methods=['DELETE'])
def delete_subscription(sub_id):
    data = request.get_json()

    user_id = data.get('user_id')

    if not user_id:
        return jsonify({'error': 'user_id is required'}), 400

    conn = get_db()
    cur = conn.cursor()

    # Удаляем подписку
    cur.execute(
        "DELETE FROM subscriptions WHERE id = %s AND user_id = %s",
        (sub_id, user_id)
    )

    if cur.rowcount == 0:
        cur.close()
        conn.close()
        return jsonify({'error': 'Subscription not found'}), 404

    # Логируем в аудит
    cur.execute(
        "INSERT INTO audit_log (user_id, action) VALUES (%s, %s)",
        (user_id, 'DELETE_SUBSCRIPTION')
    )

    conn.commit()
    cur.close()
    conn.close()

    return jsonify({'message': 'Subscription deleted successfully'})


if __name__ == '__main__':
    app.run(debug=False, port=5000)