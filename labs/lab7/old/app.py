from flask import Flask, request, jsonify, render_template
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import json

app = Flask(__name__)
limiter = Limiter(get_remote_address, app=app, default_limits=["100 per day"])

# Загружаем данные
try:
    with open('data.json') as f:
        data = json.load(f)
except:
    data = {}


def save():
    with open('data.json', 'w') as f:
        json.dump(data, f)


# Главная страница
@app.route('/')
def index():
    return render_template('index.html')


# Формы для HTML (без JSON)
@app.route('/set_form', methods=['POST'])
@limiter.limit("10 per minute")
def set_form():
    key = request.form.get('key')
    value = request.form.get('value')

    if not key or not value:
        return render_template('index.html', result={
            'status': 'error',
            'message': 'Ошибка: заполните оба поля'
        })

    # ПРОВЕРКА: если ключ уже существует
    if key in data:
        return render_template('index.html', result={
            'status': 'error',
            'message': f'Ошибка: ключ "{key}" уже существует'
        })

    data[key] = value
    save()
    return render_template('index.html', result={
        'status': 'ok',
        'message': f'Ключ "{key}" добавлен'
    })


@app.route('/get_form', methods=['GET'])
def get_form():
    key = request.args.get('key')

    if not key:
        return render_template('index.html', result={
            'status': 'error',
            'message': 'Ошибка: введите ключ'
        })

    if key in data:
        return render_template('index.html', result={
            'status': 'ok',
            'message': f'{key} = {data[key]}'
        })
    else:
        return render_template('index.html', result={
            'status': 'error',
            'message': f'Ключ "{key}" не найден'
        })


@app.route('/exists_form', methods=['GET'])
def exists_form():
    key = request.args.get('key')

    if not key:
        return render_template('index.html', result={
            'status': 'error',
            'message': 'Ошибка: введите ключ'
        })

    if key in data:
        return render_template('index.html', result={
            'status': 'ok',
            'message': f'Ключ "{key}" существует'
        })
    else:
        return render_template('index.html', result={
            'status': 'error',
            'message': f'Ключ "{key}" не существует'
        })


@app.route('/delete_form', methods=['POST'])
@limiter.limit("10 per minute")
def delete_form():
    key = request.form.get('key')

    if not key:
        return render_template('index.html', result={
            'status': 'error',
            'message': 'Ошибка: введите ключ'
        })

    if key in data:
        del data[key]
        save()
        return render_template('index.html', result={
            'status': 'ok',
            'message': f'Ключ "{key}" удален'
        })
    else:
        return render_template('index.html', result={
            'status': 'error',
            'message': f'Ключ "{key}" не найден'
        })


@app.route('/set', methods=['POST'])
@limiter.limit("10 per minute")
def set_route():
    key = request.json.get('key')
    value = request.json.get('value')

    if not key or not value:
        return jsonify({'error': 'Both key and value are required'}), 400

    if key in data:
        return jsonify({'error': f'Key "{key}" already exists'}), 400

    data[key] = value
    save()
    return jsonify({'status': 'ok'})


@app.route('/get/<key>', methods=['GET'])
def get_route(key):
    return jsonify({'value': data.get(key)})


@app.route('/delete/<key>', methods=['DELETE'])
@limiter.limit("10 per minute")
def delete_route(key):
    if key in data:
        del data[key]
        save()
        return jsonify({'status': 'deleted'})
    return jsonify({'error': 'not found'}), 404


@app.route('/exists/<key>', methods=['GET'])
def exists_route(key):
    return jsonify({'exists': key in data})


if __name__ == '__main__':
    app.run(debug=False)