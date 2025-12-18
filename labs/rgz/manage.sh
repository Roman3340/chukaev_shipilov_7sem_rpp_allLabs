#!/bin/bash

echo "=== Менеджер подписок API ==="

#setup_database() {
#    echo "Настройка базы данных PostgreSQL..."
#
#    PSQL_PATH="/c/Program Files/PostgreSQL/16/bin/psql.exe"
#
#    export PGPASSWORD='123'
#
#    echo "Создание базы данных..."
#    "$PSQL_PATH" -U postgres -h localhost -c "CREATE DATABASE subscriptions_db;" 2>/dev/null || echo "База данных уже существует"
#
#    echo "Создание пользователя..."
#    "$PSQL_PATH" -U postgres -h localhost -c "CREATE USER flask_user WITH PASSWORD 'flask_password';" 2>/dev/null || echo "Пользователь уже существует"
#
#    echo "Назначение прав..."
#    "$PSQL_PATH" -U postgres -h localhost -c "GRANT ALL PRIVILEGES ON DATABASE subscriptions_db TO flask_user;"
#
#    echo "Создание таблиц..."
#
#    SQL="
#    CREATE TABLE IF NOT EXISTS users (
#        id SERIAL PRIMARY KEY,
#        username VARCHAR(80) UNIQUE NOT NULL,
#        password_hash VARCHAR(200) NOT NULL,
#        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
#    );
#
#    CREATE TABLE IF NOT EXISTS subscriptions (
#        id SERIAL PRIMARY KEY,
#        name VARCHAR(100) NOT NULL,
#        amount DECIMAL(10,2) NOT NULL,
#        periodicity VARCHAR(20) NOT NULL,
#        start_date DATE NOT NULL,
#        user_id INTEGER REFERENCES users(id) ON DELETE CASCADE
#    );
#
#    CREATE TABLE IF NOT EXISTS audit_log (
#        id SERIAL PRIMARY KEY,
#        user_id INTEGER REFERENCES users(id),
#        action VARCHAR(50) NOT NULL,
#        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#        details TEXT
#    );
#    "
#
#    echo "$SQL" | "$PSQL_PATH" -U postgres -h localhost -d subscriptions_db
#
#    # Даем права на последовательности
#    "$PSQL_PATH" -U postgres -h localhost -d subscriptions_db -c "GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO flask_user;"
#    "$PSQL_PATH" -U postgres -h localhost -d subscriptions_db -c "GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO flask_user;"
#
#    echo "База данных настроена!"
#}

setup_database() {
    echo "Настройка базы данных PostgreSQL..."

    # Определяем окружение
    if [ -n "$GITHUB_ACTIONS" ]; then
        PSQL_PATH="psql"
        DB_PASSWORD='postgres'
        echo "Режим: CI/CD (GitHub Actions)"
    else
        PSQL_PATH="/c/Program Files/PostgreSQL/16/bin/psql.exe"
        DB_PASSWORD='123'
        echo "Режим: Локальный (Windows)"
    fi

    DB_HOST="${DB_HOST:-localhost}"
    DB_ADMIN_USER="${DB_ADMIN_USER:-postgres}"
    DB_ADMIN_PASS="${DB_ADMIN_PASS:-$DB_PASSWORD}"
    DB_NAME="${DB_NAME:-subscriptions_db}"
    DB_APP_USER="${DB_APP_USER:-flask_user}"
    DB_APP_PASS="${DB_APP_PASS:-flask_password}"

    export PGPASSWORD="$DB_ADMIN_PASS"


    echo "🗄Создание базы данных..."
    "$PSQL_PATH" -h "$DB_HOST" -U "$DB_ADMIN_USER" -c "CREATE DATABASE $DB_NAME;" 2>/dev/null || echo "База данных уже существует"

    echo "Создание пользователя..."
    "$PSQL_PATH" -h "$DB_HOST" -U "$DB_ADMIN_USER" -c "CREATE USER $DB_APP_USER WITH PASSWORD '$DB_APP_PASS';" 2>/dev/null || echo "Пользователь уже существует"

    echo "Назначение прав..."
    "$PSQL_PATH" -h "$DB_HOST" -U "$DB_ADMIN_USER" -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_APP_USER;"

    echo "Создание таблиц..."

    SQL="
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        username VARCHAR(80) UNIQUE NOT NULL,
        password_hash VARCHAR(200) NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS subscriptions (
        id SERIAL PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        amount DECIMAL(10,2) NOT NULL,
        periodicity VARCHAR(20) NOT NULL,
        start_date DATE NOT NULL,
        user_id INTEGER REFERENCES users(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS audit_log (
        id SERIAL PRIMARY KEY,
        user_id INTEGER REFERENCES users(id),
        action VARCHAR(50) NOT NULL,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        details TEXT
    );

    -- Даем права пользователю flask_user
    GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO $DB_APP_USER;
    GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO $DB_APP_USER;
    "

    echo "$SQL" | "$PSQL_PATH" -h "$DB_HOST" -U "$DB_ADMIN_USER" -d "$DB_NAME"

    echo "База данных настроена!"
}

install_dependencies() {
    echo "Установка зависимостей Python..."

    # Проверяем существует ли venv
    if [ -d "venv" ]; then
        echo "Виртуальное окружение уже существует, обновляем зависимости..."
    else
        echo "Создание виртуального окружения..."
        python3 -m venv venv || python -m venv venv
    fi

    # Активация и установка
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
    else
        source venv/Scripts/activate
    fi

    pip install --upgrade pip
    pip install -r requirements.txt

    echo "Зависимости установлены!"
}

start_app() {
    echo "Запуск Flask приложения..."

    # Проверка установленных зависимостей
    if [ ! -d "venv" ]; then
        echo "Ошибка: Сначала установите зависимости: ./manage.sh install"
        exit 1
    fi

    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
    else
        source venv/Scripts/activate
    fi

    # Проверка запущено ли уже
    if [ -f "app.pid" ] && kill -0 $(cat app.pid) 2>/dev/null; then
        echo "Приложение уже запущено (PID: $(cat app.pid))"
        exit 1
    fi

    # Запуск в фоне с логированием
    python app.py > app.log 2>&1 &
    echo $! > app.pid

    echo "Приложение запущено (PID: $(cat app.pid))"
    echo "Логи: app.log"
    echo "URL: http://localhost:5000"
}

stop_app() {
    echo "Остановка приложения..."

    if [ -f "app.pid" ]; then
        PID=$(cat app.pid)
        if kill -0 $PID 2>/dev/null; then
            kill $PID
            echo "Приложение остановлено (PID: $PID)"
        else
            echo "Процесс не найден"
        fi
        rm -f app.pid
    else
        echo "Файл PID не найден"
        if tasklist //FI "PID eq $(cat app.pid 2>/dev/null)" 2>/dev/null | grep -q "python.exe"; then
            echo "Приложение запущено, останавливаю..."
        else
            echo "Приложение не запущено"
        fi
    fi
}

run_tests() {
    echo "Запуск тестов..."

    # Простая проверка
    if [ ! -d "venv" ]; then
        echo "Ошибка: Выполните сначала ./manage.sh install"
        exit 1
    fi

    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
    else
        source venv/Scripts/activate
    fi

    # Установка pytest
    pip install pytest 2>/dev/null || true

    # Запуск тестов
    echo "Выполнение тестов..."
    if python -m pytest tests/ -v; then
        echo "Тесты пройдены успешно"
    else
        echo "Тесты завершились с ошибками"
        exit 1
    fi
}

# Показ справки если нет аргументов
if [ $# -eq 0 ]; then
    echo "Использование: ./manage.sh {команда}"
    echo ""
    echo "Команды:"
    echo "  setup_db   - Настройка базы данных PostgreSQL"
    echo "  install    - Установка зависимостей Python"
    echo "  start      - Запуск Flask приложения"
    echo "  stop       - Остановка Flask приложения"
    echo "  test       - Запуск тестов"
    exit 1
fi

# Обработка команд
case $1 in
    setup_db) setup_database ;;
    install) install_dependencies ;;
    start) start_app ;;
    stop) stop_app ;;
    test) run_tests ;;
    *)
        echo "Неизвестная команда: $1"
        echo "Использование: ./manage.sh {setup_db|install|start|stop|test}"
        exit 1
        ;;
esac