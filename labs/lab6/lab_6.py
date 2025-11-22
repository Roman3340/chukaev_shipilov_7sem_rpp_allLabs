from flask import Flask, jsonify
import sys

app = Flask(__name__)

instance_id = None


@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'instance_id': instance_id,
        'port': app.config.get('PORT', 'unknown')
    })


@app.route('/process')
def process():
    return jsonify({
        'instance_id': instance_id,
        'message': 'Запрос обработан'
    })


@app.route('/')
def home():
    return f"Инстанс {instance_id} запущен на порте {app.config.get('PORT', 'unknown')}"


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Необходимо использовать: python lab_6.py <instance_id> <port>")
        sys.exit(1)

    instance_id = sys.argv[1]
    port = int(sys.argv[2])

    app.config['PORT'] = port
    app.run(host='0.0.0.0', port=port, debug=False)