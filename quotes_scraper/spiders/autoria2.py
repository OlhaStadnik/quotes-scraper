import scrapy
from datetime import datetime
import re
from quotes_scraper.items import AutoRiaItem


class AutoriaSpider(scrapy.Spider):
    """
    Spider для збору даних про б/в автомобілі з auto.ria.com
    """
    name = "autoria"
    allowed_domains = ["auto.ria.com"]
    
    # Стартова сторінка - б/в авто
    start_urls = ["https://auto.ria.com/uk/car/used/"]
    
    # Користувацькі налаштування
    custom_settings = {
        'ROBOTSTXT_OBEY': False,  # AutoRia блокує ботів через robots.txt
        'DOWNLOAD_DELAY': 1,  # Затримка 1 секунда між запитами (ввічливо)
        'CONCURRENT_REQUESTS': 8,  # Кількість паралельних запитів
    }

    def parse(self, response):
        """
        Парсимо список оголошень на головній сторінці
        
        Args:
            response: Відповідь від сервера з HTML сторінкою
            
        Yields:
            scrapy.Request: Запити на сторінки окремих оголошень
        """
        # Знаходимо всі посилання на оголошення
        car_links = response.css('div.content-bar a.address::attr(href)').getall()
        
        # Переходимо на кожне оголошення
        for link in car_links:
            # Створюємо повний URL
            full_url = response.urljoin(link)
            # Відправляємо запит на сторінку оголошення
            yield scrapy.Request(
                url=full_url,
                callback=self.parse_car_page,
                errback=self.handle_error
            )
        
        # Пагінація - переходимо на наступну сторінку
        next_page = response.css('a.page-link.js-next::attr(href)').get()
        if next_page:
            yield scrapy.Request(
                url=response.urljoin(next_page),
                callback=self.parse
            )

    def parse_car_page(self, response):
        """
        Парсимо детальну сторінку одного оголошення
        
        Args:
            response: Відповідь з HTML окремого оголошення
            
        Yields:
            AutoRiaItem: Об'єкт з усіма зібраними даними
        """
        item = AutoRiaItem()
        
        # 1. URL оголошення
        item['url'] = response.url
        
        # 2. Назва (марка, модель, рік)
        item['title'] = response.css('h1.head::text').get()
        if item['title']:
            item['title'] = item['title'].strip()
        
        # 3. Ціна в доларах
        price_text = response.css('div.price_value strong::text').get()
        item['price_usd'] = self.extract_price(price_text)
        
        # 4. Пробіг (перетворюємо "95 тис." в 95000)
        odometer_text = response.css('div.base-information span.size18::text').get()
        item['odometer'] = self.extract_odometer(odometer_text)
        
        # 5. Ім'я продавця
        item['username'] = response.css('div.seller_info_name::text').get()
        if item['username']:
            item['username'] = item['username'].strip()
        
        # 6. Телефон (недоступний без JavaScript)
        item['phone_number'] = None  # Requires JavaScript interaction
        
        # 7. URL головного фото
        item['image_url'] = response.css('div.photo-620x465 img::attr(src)').get()
        
        # 8. Кількість фото
        photos_text = response.css('div.count strong::text').get()
        item['images_count'] = self.extract_number(photos_text)
        
        # 9. Номерний знак
        item['car_number'] = response.css('span.state-num::text').get()
        if item['car_number']:
            item['car_number'] = item['car_number'].strip()
        
        # 10. VIN код
        item['car_vin'] = response.css('span.label-vin::text').get()
        if item['car_vin']:
            item['car_vin'] = item['car_vin'].strip()
        
        # 11. Дата збереження
        item['datetime_found'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        yield item

    def extract_price(self, price_text):
        """
        Витягує ціну з тексту і конвертує в число
        
        Args:
            price_text: Рядок типу "51 500 $"
            
        Returns:
            int: Ціна як число або None
        """
        if not price_text:
            return None
        
        # Видаляємо всі символи крім цифр
        numbers = re.findall(r'\d+', price_text)
        if numbers:
            # З'єднуємо всі цифри і конвертуємо в число
            return int(''.join(numbers))
        return None

    def extract_odometer(self, odometer_text):
        """
        Витягує пробіг і конвертує в кілометри
        
        Args:
            odometer_text: Рядок типу "95 тис. км" або "199 тис."
            
        Returns:
            int: Пробіг в км як число (95000) або None
        """
        if not odometer_text:
            return None
        
        # Шукаємо число і "тис" (тисяч)
        match = re.search(r'(\d+)\s*тис', odometer_text)
        if match:
            # Конвертуємо тисячі в повне число
            return int(match.group(1)) * 1000
        
        # Якщо немає "тис", просто витягуємо число
        numbers = re.findall(r'\d+', odometer_text)
        if numbers:
            return int(''.join(numbers))
        
        return None

    def extract_number(self, text):
        """
        Витягує число з тексту
        
        Args:
            text: Рядок що містить число
            
        Returns:
            int: Витягнуте число або None
        """
        if not text:
            return None
        
        numbers = re.findall(r'\d+', text)
        if numbers:
            return int(numbers[0])
        return None

    def handle_error(self, failure):
        """
        Обробка помилок при завантаженні сторінок
        
        Args:
            failure: Об'єкт з інформацією про помилку
        """
        self.logger.error(f'Request failed: {failure.request.url}')
        self.logger.error(f'Error: {failure.value}')