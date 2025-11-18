from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import csv

import database

import time


# Подключаем базу
db = database.BaseDB(True)

# Настройка подключения к Selenium Server в Docker
selenium_url = "http://localhost:4444/wd/hub"

# Настраиваем опции для Chrome
chrome_options = Options()
chrome_options.add_argument("--no-sandbox")  # Для работы в Docker
chrome_options.add_argument("--disable-dev-shm-usage")  # Для работы в Docker

# Заголовок 
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}

url = input('URL для скана:')
pages = int(input('Количество страниц (число):'))


def getLinks():
    
    # Инициализируем драйвер
    driver = webdriver.Remote(
        command_executor=selenium_url,
        options=chrome_options
    )

    test_url = 'https://chromewebstore.google.com/search/highlight?_category=extensions&pli=1'

    # Открываем страницу
    driver.get(url)
    time.sleep(3)  # Ждём загрузки

    pattern = 'https://support.google.com/chrome_webstore/answer/12225786?p=cws_reviews_results&hl=en-US'
    webstore_link = 'https://chromewebstore.google.com/detail'

    # Ждём появления h1
    h1 = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "h1"))
    )

    for i in tqdm(range(pages), bar_format="{l_bar}{bar:20}{r_bar}", colour="green"):

        # Находим все ссылки после h1
        h1 = driver.find_element(By.TAG_NAME, "h1")
        next_element = h1.find_element(By.XPATH, "./following-sibling::*[1]")
        link_children = next_element.find_elements(By.TAG_NAME, "a")[-40:]

        for link in link_children:
            href = link.get_attribute("href")
            if href and href != pattern and webstore_link in href and db.findLinkBase(href):
                #print("Ссылка:", href)
                db.addTable( 
                            link=href, 
                            name=None, 
                            autor=None, 
                            rating=None, 
                            description=None, 
                            app_link=None, 
                            len_ratings=None, 
                            len_users=None)

        # Нажимаем кнопку "Load more"
        button = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.XPATH, "//button[.//span[text()='Load more']]"))
        )
        driver.execute_script("arguments[0].scrollIntoView();", button)
        button.click()

        time.sleep(10)

    # Закрываем браузер
    driver.quit()


def getDetail():
    all_link_count = db.getCountAll()
    with tqdm(total=all_link_count, bar_format="{l_bar}{bar:20}{r_bar}", colour="green", desc="Обработка") as pbar:
        while True:
            app = db.findNewLinkBase()

            if not app:
                #print("...Детали получены...")
                return

            html = urlRequest(app.link)
            if not html:
                print(f"Failed to get HTML for {app.link}")
                return

            soup = BeautifulSoup(html, 'html.parser')

            # --- Начинаем парсинг ---

            # Название (из h1)
            try:
                name = soup.find('h1').get_text(strip=True)
            except AttributeError:
                name = None
            #print(f"Название: {name}")

            # Автор
            try:
                author_div = soup.find('div', class_="mdSapd")
                if author_div:
                    # Получаем все содержимое div и берем текст до первого <br>
                    author = ''.join(str(x) for x in author_div.contents if x.name != 'br').strip()
                    # Если есть <br>, то берем только текст до него
                    if author_div.find('br'):
                        author = author_div.find('br').previous_sibling.strip()
                    else:
                        author = author_div.get_text(strip=True)
                else:
                    author = None
            except (AttributeError, ValueError, IndexError, TypeError):
                author = None
            #print(f"Автор: {author}")

            # Рейтинг (из span с классом GlMWqe)
            try:
                rating_text = soup.find('h2', class_='Yemige').get_text(strip=True)
                rating = float(rating_text.split(' ')[0].replace(',', '.'))
            except (AttributeError, ValueError, IndexError, TypeError):
                rating = None
            #print(f"Рейтинг: {rating}")

            # Количество оценок
            try:
                len_ratings_text = soup.find('h2', class_='Yemige').find_all('span', recursive=False)[1].get_text(strip=True)
                len_ratings = len_ratings_text
            except (AttributeError, ValueError, IndexError, TypeError):
                len_ratings = None
            #print(f"Количество оценок: {len_ratings}")

            # Количество пользователей
            try:
                users_text = soup.find_all(
                                    lambda tag: tag.name == 'a' and '/category/extensions' in tag.get('href', '')
                                )[0].parent
                # Убираем '+' и пробелы, затем преобразуем в число
                len_users = str(users_text).split('</a>')[2].replace('пользователей</div>','').replace('пользователя</div>','').replace('пользователь</div>','')
            except (AttributeError, ValueError, IndexError, TypeError):
                len_users = None
            #print(f"Количество пользователей: {len_users}")

            # Ссылка приложения
            try:
                # Извлекаем полный текст из блока описания
                link_app_div = soup.find('h1').parent.parent.parent.find_all('a')[2].get('href', '')
                if link_app_div:            
                    # paragraphs = link_app_div.find_all('p')
                    # link_app = '\n'.join(p.get_text(strip=True) for p in paragraphs)
                    link_app = link_app_div
                else:
                    link_app = None
            except (AttributeError, ValueError, IndexError, TypeError):
                link_app = None

            #print(f"ссылка приложения: {link_app}")

            #Описание
            try:
                # Извлекаем полный текст из блока описания
                description_div = soup.find_all(
                                    lambda tag: tag.name == 'h2' and 'Обзор' in tag.get_text(strip=True)
                                )[0].parent.parent
                if description_div:
                    # Собираем текст из всех параграфов внутри блока
                    paragraphs = description_div.find_all('p')
                    description = '\n'.join(p.get_text(strip=True) for p in paragraphs)
                else:
                    description = None
            except (AttributeError, ValueError, IndexError, TypeError):
                description = None
            #print(f"Описание: {description}")

            db.editLinkDescription(app.id, name, author, rating, description, link_app, len_ratings, len_users)
            pbar.update(1)


def urlRequest(url):
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        html_content = response.text        
    else:
        print(f"Ошибка: {response.status_code}")

    # with open("output.txt", "w", encoding="utf-8") as file:
    #     file.write(html_content)

    return html_content


def saveCsv():
    apps = db.getAllData()

    # Определяем заголовки (ключи первого словаря)
    headers = apps[0].to_dict().keys() if apps else []

    # Путь к CSV-файлу
    csv_path = "app.csv"

    # Записываем данные в CSV
    with open(csv_path, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()  # Записываем заголовки

        for item in apps:
            writer.writerow(item.to_dict())  # Записываем одну строку


def main():
    print('Собр ссылок:')
    getLinks()
    print('Получаем детали:')
    getDetail()
    print('Формируем CSV')
    saveCsv()
    print('--- все теперь можно скамить ---')


# Запуск только при прямом выполнении скрипта
if __name__ == "__main__":
    main()