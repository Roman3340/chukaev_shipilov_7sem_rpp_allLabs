from flask import Flask, jsonify, request, render_template, redirect, url_for
import requests
import threading
import time

app = Flask(__name__)

instances = []
active_instances = []
current_index = 0
error_message = ""


def health_checker():
    while True:
        time.sleep(5)
        check_instances_health()


def check_instances_health():
    global active_instances, current_index

    healthy_instances = []

    for instance in instances:
        try:
            response = requests.get(f"http://{instance['ip']}:{instance['port']}/health", timeout=2)
            if response.status_code == 200:
                healthy_instances.append(instance)
                print(f"Инстанс {instance['ip']}:{instance['port']} - здоров")
            else:
                print(f"Инстанс {instance['ip']}:{instance['port']} - нездоров")
        except Exception as e:
            print(f"Инстанс {instance['ip']}:{instance['port']} - недоступен. Ошибка: {e}")

    active_instances = healthy_instances
    current_index = 0


def get_next_instance():
    if not active_instances:
        return None

    global current_index
    instance = active_instances[current_index]
    current_index = (current_index + 1) % len(active_instances)
    return instance


@app.route('/health')
def lb_health():
    check_instances_health()

    return jsonify({
        'status': 'started',
        'total_instances': len(instances),
        'active_instances': len(active_instances),
        'instances': instances
    })


@app.route('/process')
def lb_process():
    instance = get_next_instance()

    if not instance:
        return jsonify({'error': 'No available instances'}), 503

    try:
        response = requests.get(f"http://{instance['ip']}:{instance['port']}/process", timeout=5)
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({'error': f'Ошибка: {e}'}), 502


@app.route('/add_instance', methods=['POST'])
def add_instance():
    global error_message
    ip = request.form.get('ip')
    port = request.form.get('port')

    if not ip or not port:
        error_message = "Необходимо указать IP и порт"
        return redirect('/')

    try:
        port = int(port)
    except ValueError:
        error_message = "Порт должен быть числом"
        return redirect('/')

    new_instance = {
        'ip': ip,
        'port': port
    }

    for instance in instances:
        if instance['ip'] == new_instance['ip'] and instance['port'] == new_instance['port']:
            error_message = "Такой инстанс уже существует"
            return redirect('/')

    try:
        response = requests.get(f"http://{ip}:{port}/health", timeout=2)
        if response.status_code == 200:
            instances.append(new_instance)
            check_instances_health()
        else:
            error_message = "Инстанс недоступен - не добавлен"
    except:
        error_message = "Инстанс недоступен - не добавлен"
    return redirect('/')


@app.route('/remove_instance', methods=['POST'])
def remove_instance():
    index_str = request.form.get('index')

    if not index_str:
        return redirect('/')

    try:
        index = int(index_str)
    except ValueError:
        return redirect('/')

    if index < 0 or index >= len(instances):
        return redirect('/')

    del instances[index]
    check_instances_health()
    return redirect('/')

@app.route('/')
def mainFunc():
    global error_message
    check_instances_health()
    error_to_show = error_message
    error_message = ""
    return render_template('index.html', instances=instances,
                           active_instances=active_instances,
                           error_message=error_to_show)

@app.route('/<path:path>')
def catch_all(path):
    instance = get_next_instance()

    if not instance:
        return jsonify({'error': 'No available instances'}), 503

    try:
        response = requests.get(f"http://{instance['ip']}:{instance['port']}/{path}", timeout=5)
        if response.status_code == 404:
            return jsonify({
                'error': f'Route /{path} not found on instance {instance["ip"]}:{instance["port"]}'
            }), 404
        try:
            return jsonify(response.json()), response.status_code
        except ValueError:
            return response.text, response.status_code
    except Exception as e:
        return jsonify({'error': f'Error: {e}'}), 502


if __name__ == '__main__':
    health_thread = threading.Thread(target=health_checker, daemon=True)
    health_thread.start()

    app.run(host='0.0.0.0', port=8000, debug=False)