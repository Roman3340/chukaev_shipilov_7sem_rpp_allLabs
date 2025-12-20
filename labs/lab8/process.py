import asyncio
import json
from collections import defaultdict


async def process_transactions():
    try:
        with open('transactions.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Ошибка: {e}")
        return

    print(f"Обработка {len(data)} транзакций...\n")

    category_totals = defaultdict(float)
    alerts_shown = set()

    for i, transaction in enumerate(data, 1):
        await asyncio.sleep(0.01)

        category = transaction['category']
        amount = transaction['amount']

        old_total = category_totals[category]
        category_totals[category] += amount

        if old_total <= 6000 < category_totals[category] and category not in alerts_shown:
            alerts_shown.add(category)
            print(f"Категория '{category}' превысила 6000 руб. "
                  f"({category_totals[category]:.2f} руб.)")

    print("РЕЗУЛЬТАТЫ:")

    total_all = 0
    for category in sorted(category_totals.keys()):
        total = category_totals[category]
        total_all += total
        print(f"{category:15} {total:10.2f} руб.")

    print(f"ОБЩАЯ СУММА: {total_all:10.2f} руб.")
    print(f"Категорий: {len(category_totals)}")


async def main():
    await process_transactions()


if __name__ == "__main__":
    asyncio.run(main())