# Chrome Web Store Parser

**Описание**Скрипт для парсинга расширений из Chrome Web Store. Собирает ссылки на расширения, их названия, авторов, рейтинги, описания, количество пользователей и ссылки на приложения. Данные сохраняются в базу данных и экспортируются в CSV.

---

## Требования

- Python 3.8+
- Docker (для запуска Selenium Server)
- Библиотеки:

```Bash  

	    Package            Version
	------------------ -----------
	attrs              25.4.0
	beautifulsoup4     4.14.2
	bs4                0.0.2
	certifi            2025.11.12
	charset-normalizer 3.4.4
	h11                0.16.0
	idna               3.11
	outcome            1.3.0.post0
	pip                25.0
	PySocks            1.7.1
	requests           2.32.5
	selenium           4.38.0
	sniffio            1.3.1
	sortedcontainers   2.4.0
	soupsieve          2.8
	SQLAlchemy         2.0.44
	tqdm               4.67.1
	trio               0.32.0
	trio-websocket     0.12.2
	typing_extensions  4.15.0
	urllib3            2.5.0
	websocket-client   1.9.0
	wsproto            1.3.1

```    

---

## Установка и запуск
1. **Установите Docker**:
Подробная инструкция https://docs.docker.com/engine/install/
```bash
	sudo apt update
	sudo apt install -y docker-ce docker-ce-cli containerd.io

```

2. **Запустите Selenium Server в Docker**:
есть моменты по архитектуре камня
```bash

	docker run -d -p 4444:4444 --name selenium selenium/standalone-chrome

	# или для arm архитектуры
	docker run -d --platform linux/arm64 -p 4444:4444 --name selenium selenium/standalone-chrome

```

3. **Создаем виртуальное окружение и активируем его**:
```bash

	python3 -m venv venv
	source venv/bin/activate

```

4. **Устанавливаем нужные модули**:
```bash

	pip install selenium beautifulsoup4 tqdm requests

```

6. **Запустите скрипт**:
```bash

    > python parser.py    

```

7. **CSV фаил и данные**:
- app.csv сохраненные данные при новом запуске его лучше удалить
- также можно просмотреть полученную информацию SQLite базе template.db ( автоматически удаляется при каждом запуске парсера )


---

## Структура проекта

```

	.
	├── app.csv
	├── database.py
	├── links.txt
	├── model.py
	├── out.txt
	├── parser.py <-- точка входа
	├── README.md
	└── template.db

```

---

## Функционал

- **Сбор ссылок**: Парсит ссылки на расширения с указанного количества страниц.
- **Детализация**: Извлекает название, автора, рейтинг, описание, количество пользователей и ссылку на приложение.
- **Экспорт**: Сохраняет данные в CSV.

---

## Пример использования

python

Copy
```bash

	$ python parser.py
	Ссылка для скана: https://chromewebstore.google.com/search/highlight?_category=extensions&pli=1
	Количество страниц (число): 2
	Собр ссылок:
	100%|██████████| 2/2 [00:10<00:00]
	Получаем детали:
	100%|██████████| 50/50 [00:30<00:00]
	Формируем CSV:
	--- все теперь можно скамить ---

```

---

## Планы по развитию

- Оптимизация скорости парсинга.
- Переход на PostgreSQL
- Асинхронный парсинг url и деталей 


---

## Примечания

- Для корректной работы требуется стабильное интернет-соединение.
- Возможны задержки из-за ограничений Chrome Web Store.