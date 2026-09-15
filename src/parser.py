import requests
from bs4 import BeautifulSoup
import json

URL = "https://schedule.artmexanika.ru/theatre"

def parse_schedule():
    # Имитируем обычный браузер, чтобы сайт не блокировал запрос
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(URL, headers=headers, timeout=10)
        response.raise_for_status()  # Ошибка, если статус не 200
    except requests.RequestException as e:
        print(f"Ошибка при запросе страницы: {e}")
        return []

    soup = BeautifulSoup(response.text, "lxml")

    # Тут нужно попасть в реальные элементы таблицы/списка.
    # Поскольку точной структуры таблицы я не вижу, используем универсальный подход:
    # ищем строки, где есть дата и название — обычно это <tr> или <div> с похожими классами.
    events = []

    # Вариант 1: если это таблица (<table>)
    table = soup.find("table")
    if table:
        rows = table.find_all("tr")[1:]  # пропускаем заголовок
        for row in rows:
            cols = row.find_all(["td", "th"])
            if len(cols) < 2:
                continue
            # Пример: дата в первом столбце, название во втором
            date_str = cols[0].get_text(strip=True)
            title = cols[1].get_text(strip=True)
            events.append({
                "date": date_str,
                "title": title,
                "source": "table"
            })

    # Вариант 2: если это список блоков (частый случай на современных сайтах)
    # Подбирай селектор под реальную структуру: .event-item, .performance, .row и т.п.
    blocks = soup.select(".event-item, .performance, .schedule-row, div[data-date]")
    for block in blocks:
        date_el = block.select_one("[data-date], .date, .event-date")
        title_el = block.select_one(".title, .event-title, h3, h2")
        if date_el and title_el:
            events.append({
                "date": date_el.get_text(strip=True),
                "title": title_el.get_text(strip=True),
                "source": "blocks"
            })

    return events

if __name__ == "__main__":
    data = parse_schedule()
    print(f"Найдено событий: {len(data)}")
    # Вывод первых 5 для проверки
    for i, ev in enumerate(data[:5], 1):
        print(f"{i}. {ev['date']} — {ev['title']}")

    # Сохраняем всё в JSON рядом с main.py
    with open("schedule.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("\nДанные сохранены в schedule.json")
