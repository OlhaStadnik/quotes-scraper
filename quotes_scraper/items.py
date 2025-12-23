# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

class AutoRiaItem(scrapy.Item):
    url = scrapy.Field()
    title = scrapy.Field()
    price_usd = scrapy.Field()  # int
    odometer = scrapy.Field()  # int
    username = scrapy.Field()
    phone_number = scrapy.Field()  # int
    image_url = scrapy.Field()
    images_count = scrapy.Field()  # int
    car_number = scrapy.Field()
    car_vin = scrapy.Field()
    datetime_found = scrapy.Field()  # datetime
