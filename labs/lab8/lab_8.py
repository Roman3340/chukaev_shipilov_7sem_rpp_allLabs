import asyncio
import json
import random
from datetime import datetime
import sys

CATEGORIES = ["еда", "транспорт", "развлечения", "покупки", "здоровье"]
FILENAME = "transactions.json"


def get_next_id():
    try:
        with open(FILENAME, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if data:
                max_id = max(item['id'] for item in data)
                return max_id + 1
    except:
        pass
    return 1


async def save_batch(batch, batch_number):
    try:
        with open(FILENAME, 'r', encoding='utf-8') as f:
            existing_data = json.load(f)
    except:
        existing_data = []

    existing_data.extend(batch)

    with open(FILENAME, 'w', encoding='utf-8') as f:
        json.dump(existing_data, f, indent=2, ensure_ascii=False)

    print(f"Сохранен батч {batch_number} ({len(batch)} транзакций)")


async def generate_transactions(count):
    start_id = get_next_id()
    batch = []
    batch_number = 1

    print(f"Генерация {count} транзакций, начиная с ID={start_id}...")

    for i in range(start_id, start_id + count):
        transaction = {
            "id": i,
            "timestamp": datetime.now().isoformat(),
            "category": random.choice(CATEGORIES),
            "amount": round(random.uniform(50, 5000), 2)
        }

        batch.append(transaction)

        if len(batch) == 10:
            await save_batch(batch, batch_number)
            batch_number += 1
            batch = []
            await asyncio.sleep(0.01)

    if batch:
        await save_batch(batch, batch_number)

    print(f"\nГотово! Сгенерировано {count} транзакций")


async def main():
    """Основная функция"""
    if len(sys.argv) != 2:
        print("Использование: python lab_8.py <количество>")
        return

    try:
        count = int(sys.argv[1])
        if count <= 0:
            print("Ошибка: число должно быть положительным")
            return
    except:
        print("Ошибка: укажите число")
        return

    await generate_transactions(count)


if __name__ == "__main__":
    asyncio.run(main())