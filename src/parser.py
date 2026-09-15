from playwright.sync_api import sync_playwright
import json

URL = "https://schedule.artmexanika.ru/login"
EMAIL = "demo@artmexanika.ru"
PASSWORD = "artmexanika"

def parse_schedule():
    with sync_playwright() as p:
        # headless=False — чтобы ты видел, как браузер открывается
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        # 1. Открываем страницу логина
        page.goto(URL, wait_until="networkidle")
        page.wait_for_timeout(2000)

        # 2. Заполняем форму авторизации
        page.fill('input[type="email"]', EMAIL)
        page.fill('input[type="password"]', PASSWORD)
        page.click('button[type="submit"]')

        # 3. Ждём перехода на страницу /theatre
        page.wait_for_url("**/theatre", timeout=15000)
        page.wait_for_timeout(5000)  # даём время на загрузку расписания

        # 4. Сохраняем полный HTML для анализа
        html = page.content()
        with open("page_dump.html", "w", encoding="utf-8") as f:
            f.write(html)
        print("HTML сохранён в page_dump.html")

        # 5. Собираем все текстовые элементы внутри .calendar--body
        events = []
        elements = page.query_selector_all(".calendar--body *")
        for el in elements:
            text = el.inner_text().strip()
            if text and len(text) > 3:
                events.append({"text": text})

        browser.close()
        return events

if __name__ == "__main__":
    data = parse_schedule()
    print(f"Найдено элементов: {len(data)}")
    for i, ev in enumerate(data[:20], 1):
        print(f"{i}. {ev['text'][:120]}")
