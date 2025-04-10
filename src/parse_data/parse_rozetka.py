from uuid import uuid4
from requests_html import HTMLSession
from src.database.base import db
from src.database.models import Product

URL = "https://rozetka.com.ua/ua/igrovie-mishi/c4673278/producer=logitech/"

def get_products(url: str = URL):
    session = HTMLSession()
    response = session.get(url)

    # Проверяем статус ответа
    if response.status_code != 200:
        print(f"Ошибка: Сервер вернул статус {response.status_code}")
        print(response.text)  # Для отладки
        return

    # Парсим ссылки на товары
    try:
        products = response.html.xpath('//a[contains(@class, "goods-tile__heading")]/@href')
    except Exception as e:
        print(f"Ошибка парсинга: {e}")
        return

    for product in products:
        print(product)
        save_product(product)

    db.session.commit()

def save_product(url: str):
    session = HTMLSession()
    response = session.get(url)

    # Проверяем статус ответа
    if response.status_code != 200:
        print(f"Ошибка: Сервер вернул статус {response.status_code}")
        print(response.text)  # Для отладки
        return

    # Парсим данные о товаре
    try:
        name = response.html.xpath('//h1[contains(@class, "product__title")]/text()')[0].strip()
        price = response.html.xpath('//p[contains(@class, "product-prices__big")]/text()')[0].strip().replace(u"\xa0", "")
        img_url = response.html.xpath('//img[contains(@class, "picture-container__picture")]/@src')[0]
        description = response.html.xpath('//div[contains(@class, "product-about__description")]/text()')
        description = ''.join(description).strip() if description else "Описание отсутствует"

        # Создаем объект товара
        product = Product(
            id=uuid4().hex,
            name=name,
            description=description,
            img_url=img_url,
            price=float(price.replace('₴', '').replace(' ', ''))
        )

        db.session.add(product)
        print(f"Товар '{name}' збережено")
    except Exception as e:
        print(f"Ошибка парсинга товара: {e}")