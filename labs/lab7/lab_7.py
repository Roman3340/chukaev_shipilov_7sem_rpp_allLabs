from flask import Flask, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import json

app = Flask(__name__)
limiter = Limiter(get_remote_address, app=app, default_limits=["100 per day"])

try:
    with open('data.json') as f:
        data = json.load(f)
except:
    data = {}


def save():
    with open('data.json', 'w') as f:
        json.dump(data, f)


@app.route('/set', methods=['POST'])
@limiter.limit("10 per minute")
def set_route():
    if not request.json:
        return jsonify({'error': 'JSON required'}), 400

    key = request.json.get('key')
    value = request.json.get('value')

    if not key or not value:
        return jsonify({'error': 'Both key and value are required'}), 400

    if key in data:
        return jsonify({'error': f'Key "{key}" already exists'}), 400

    data[key] = value
    save()
    return jsonify({'status': 'ok', 'key': key, 'value': value})


@app.route('/get/<key>', methods=['GET'])
def get_route(key):
    if key in data:
        return jsonify({'key': key, 'value': data[key]})
    return jsonify({'error': f'Key "{key}" not found'}), 404


@app.route('/delete/<key>', methods=['DELETE'])
@limiter.limit("10 per minute")
def delete_route(key):
    if key in data:
        value = data[key]
        del data[key]
        save()
        return jsonify({'status': 'deleted', 'key': key, 'value': value})
    return jsonify({'error': f'Key "{key}" not found'}), 404


@app.route('/exists/<key>', methods=['GET'])
def exists_route(key):
    return jsonify({'key': key, 'exists': key in data})


if __name__ == '__main__':
    app.run(debug=False)