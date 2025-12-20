#Код №1
print("\n\nРезультат программы после рефакторинга кода №1")
def send_message(service_name, to, content_type, content):
    print(f"Connecting to {service_name}")
    print(f"Sending {content_type} to {to} with {content_type.lower()} '{content}'")
    print(f"{content_type} sent.")

def send_email(to, subject, body):
    send_message("SMTP server", to, "Email", f"subject '{subject}', body '{body}'")

def send_sms(to, message):
    send_message("SMS gateway", to, "SMS", message)

# Демонстрация работы после рефакторинга
send_email("alex@example.com", "Привет", "Как дела?")
send_sms("+79161234567", "Привет")


#Код №2
print("\n\nРезультат программы после рефакторинга кода №2")
def calculate_total(items):
    total = 0
    for item in items:
        item_price = item["price"]
        item_quantity = item["quantity"]
        total += item_price * item_quantity
    return total


def process_payment(amount):
    print(f"Processing payment for amount: {amount}")
    print("Payment successful!")


def send_confirmation():
    print("Sending confirmation email")


def process_order(order):
    order_items = order["items"]
    order_total = calculate_total(order_items)

    print(f"Total: {order_total}")

    process_payment(order_total)
    send_confirmation()

    print("Order complete.")


# Демонстрация работы после рефакторинга
order_example = {
    "items": [
        {"name": "Book", "price": 500, "quantity": 2},
        {"name": "Pen", "price": 50, "quantity": 5}
    ]
}

process_order(order_example)


#Код №3
print("\n\nРезультат программы после рефакторинга кода №3")
def calculate_shipping(country, weight):
    shipping_rates = {
        "USA": {"light": 10, "heavy": 20},
        "Canada": {"light": 15, "heavy": 25},
        "default": {"light": 30, "heavy": 50}
    }

    weight_type = "light" if weight < 5 else "heavy"

    country_rates = shipping_rates.get(country, shipping_rates["default"])

    return country_rates[weight_type]


# Демонстрация работы после рефакторинга
print("USA, 3kg:", calculate_shipping("USA", 3))
print("USA, 7kg:", calculate_shipping("USA", 7))
print("Canada, 4kg:", calculate_shipping("Canada", 4))
print("Germany, 6kg:", calculate_shipping("Germany", 6))


#Код №4
print("\n\nРезультат программы после рефакторинга кода №4")
# Константы для налоговых ставок и границ доходов
TAX_BRACKET_1_MAX = 10000 # Верхняя граница первого налогового порога
TAX_BRACKET_2_MAX = 20000 # Верхняя граница второго налогового порога
TAX_RATE_LOW = 0.10 # Ставка 10% для низких доходов
TAX_RATE_MEDIUM = 0.15 # Ставка 15% для средних доходов
TAX_RATE_HIGH = 0.20 # Ставка 20% для высоких доходов


def calculate_tax(income):
    if income <= TAX_BRACKET_1_MAX:
        return income * TAX_RATE_LOW # Налог 10% для доходов до 10000
    elif income <= TAX_BRACKET_2_MAX:
        return income * TAX_RATE_MEDIUM # Налог 15% для доходов 10001-20000
    else:
        return income * TAX_RATE_HIGH # Налог 20% для доходов выше 20000


# Демонстрация работы после рефакторинга
incomes = [8000, 15000, 25000]

for inc in incomes:
    print(f"Доход: {inc}, Налог: {calculate_tax(inc)}")



#Код №5
print("\n\nРезультат программы после рефакторинга кода №5")
def create_report(employee_data):
    report_fields = [
        ("Name", "name"),
        ("Age", "age"),
        ("Department", "department"),
        ("Salary", "salary"),
        ("Bonus", "bonus"),
        ("Performance Score", "performance_score")
    ]

    for field_name, data_key in report_fields:
        value = employee_data.get(data_key, "N/A")
        print(f"{field_name}: {value}")

# Демонстрация работы после рефакторинга
employee = {
    "name": "Иван Иванов",
    "age": 30,
    "department": "IT",
    "salary": 50000,
    "bonus": 5000,
    "performance_score": 4.5
}

create_report(employee)
