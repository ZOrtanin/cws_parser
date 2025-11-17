from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
from bs4 import BeautifulSoup

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


def getLinks():
    print('Начинаем парс ссылок')

    # Инициализируем драйвер
    driver = webdriver.Remote(
        command_executor=selenium_url,
        options=chrome_options
    )

    # Открываем страницу
    driver.get('https://chromewebstore.google.com/search/highlight?_category=extensions&pli=1')
    time.sleep(3)  # Ждём загрузки

    pattern = 'https://support.google.com/chrome_webstore/answer/12225786?p=cws_reviews_results&hl=en-US'
    webstore_link = 'https://chromewebstore.google.com/detail'

    # Ждём появления h1
    h1 = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "h1"))
    )

    for i in range(10):
        # Находим все ссылки после h1
        h1 = driver.find_element(By.TAG_NAME, "h1")
        next_element = h1.find_element(By.XPATH, "./following-sibling::*[1]")
        link_children = next_element.find_elements(By.TAG_NAME, "a")[-40:]

        for link in link_children:
            href = link.get_attribute("href")
            if href and href != pattern and webstore_link in href and db.findLinkBase(href):
                print("Ссылка:", href)
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


    # Делаем скриншот и сохраняем в файл
    # driver.save_screenshot("screenshot.png")
    # html_content = driver.page_source

    # Закрываем браузер
    driver.quit()


def getDetail():
    #while True:
    app = db.findNewLinkBase()
    if not app:
        print("No new links to process.")
        return

    html = urlRequest(app.link)
    if not html:
        print(f"Failed to get HTML for {app.link}")
        return

    soup = BeautifulSoup(html, 'html.parser')

    # --- Начинаем парсинг ---
    # Примечание: Селекторы могут потребовать корректировки, если структура сайта изменится.

    # Название (из h1)
    try:
        name = soup.find('h1', class_='Pa2dE').get_text(strip=True)
    except AttributeError:
        name = None
    print(f"Название: {name}")

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
    except AttributeError:
        author = None
    print(f"Автор: {author}")

    # Рейтинг (из span с классом GlMWqe)
    try:
        rating_text = soup.find('h2', class_='Yemige').get_text(strip=True)
        rating = float(rating_text.split(' ')[0].replace(',', '.'))
    except (AttributeError, ValueError):
        rating = None
    print(f"Рейтинг: {rating}")

    # Количество оценок
    try:
        len_ratings_text = soup.find('h2', class_='Yemige').find_all('span', recursive=False)[1].get_text(strip=True)
        len_ratings = len_ratings_text
    except (AttributeError, ValueError):
        len_ratings = None
    print(f"Количество оценок: {len_ratings}")

    # Количество пользователей
    try:
        users_text = soup.find_all(
                            lambda tag: tag.name == 'a' and '/category/extensions' in tag.get('href', '')
                        )[0].parent
        # Убираем '+' и пробелы, затем преобразуем в число
        len_users = str(users_text).split('</a>')[2].replace('пользователей</div>','')
    except (AttributeError, ValueError):
        len_users = None
    print(f"Количество пользователей: {len_users}")

    # Описание
    try:
        # Извлекаем полный текст из блока описания
        description_div = soup.find('div', class_='C-b-p-j-D')
        description = description_div.get_text('\n', strip=True) if description_div else None
    except AttributeError:
        description = None
    print(f"Описание: {description}")


    # Здесь вы бы обновили базу данных
    # db.updateTable(app.id, name=name, autor=author, rating=rating, description=description, len_ratings=len_ratings, len_users=len_users)
   
    # if not link_app:
    #     return

    # # Инициализируем драйвер
    # driver = webdriver.Remote(
    #     command_executor=selenium_url,
    #     options=chrome_options
    # )

    # # Открываем страницу
    # driver.get('https://chromewebstore.google.com/search/highlight?_category=extensions&pli=1')


def urlRequest(url):
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        html_content = response.text        
    else:
        print(f"Ошибка: {response.status_code}")

    # with open("output.txt", "w", encoding="utf-8") as file:
    #     file.write(html_content)

    return html_content

def main():
    print('Начинаем парс ссылок')
    #getLinks()
    print('Получаем детали')
    getDetail()

    

main()