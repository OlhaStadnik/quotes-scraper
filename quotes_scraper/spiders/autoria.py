import re
import scrapy
from datetime import datetime
from scrapy_playwright.page import PageMethod
from quotes_scraper.items import AutoRiaItem


class AutoRiaSpider(scrapy.Spider):
    name = "autoria"

    custom_settings = {
        "DOWNLOAD_HANDLERS": {
            "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
            "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
        },
        "TWISTED_REACTOR": "twisted.internet.asyncioreactor.AsyncioSelectorReactor",
        "PLAYWRIGHT_BROWSER_TYPE": "chromium",
        "PLAYWRIGHT_LAUNCH_OPTIONS": {
            "headless": True,
        },
    }

    def __init__(self, start_url=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start_url = start_url or "https://auto.ria.com/uk/car/used/"

    def start_requests(self):
        yield scrapy.Request(
            url=self.start_url,
            callback=self.parse_listing,
            meta={
                "playwright": True,
                "playwright_include_page": True,
                "playwright_page_methods": [
                    PageMethod("wait_for_selector", "section.ticket-item", timeout=30000),
                ],
            },
        )

    async def parse_listing(self, response):
        page = response.meta.get("playwright_page")

        # Get all car links from the listing page
        car_links = response.css("section.ticket-item a.m-link-ticket::attr(href)").getall()

        if not car_links:
            # Alternative selectors
            car_links = response.css("div.content-bar a.address::attr(href)").getall()

        if not car_links:
            car_links = response.css("a.proposition_link::attr(href)").getall()

        self.logger.info(f"Found {len(car_links)} car links on page")

        for link in car_links:
            if link and "/auto_" in link:
                full_url = response.urljoin(link)
                yield scrapy.Request(
                    url=full_url,
                    callback=self.parse_car_detail,
                    meta={
                        "playwright": True,
                        "playwright_include_page": True,
                        "playwright_page_methods": [
                            PageMethod("wait_for_load_state", "networkidle"),
                        ],
                    },
                )

        # Handle pagination
        if page:
            next_page = response.css("a.page-link.next::attr(href)").get()
            if not next_page:
                next_page = response.css("span.page-item.next a::attr(href)").get()
            if not next_page:
                next_page = response.css("a[rel='next']::attr(href)").get()

            if next_page:
                yield scrapy.Request(
                    url=response.urljoin(next_page),
                    callback=self.parse_listing,
                    meta={
                        "playwright": True,
                        "playwright_include_page": True,
                        "playwright_page_methods": [
                            PageMethod("wait_for_selector", "section.ticket-item", timeout=30000),
                        ],
                    },
                )
            await page.close()

    async def parse_car_detail(self, response):
        page = response.meta.get("playwright_page")
        item = AutoRiaItem()

        # URL
        item["url"] = response.url

        # Title
        title = response.css("h1.head::text").get()
        if not title:
            title = response.css("h1.auto-head_title::text").get()
        if not title:
            title = response.css("h3.auto-content_title::text").get()
        item["title"] = title.strip() if title else None

        # Price USD
        price_text = response.css("div.price_value strong::text").get()
        if not price_text:
            price_text = response.css("span.price_value::attr(data-main-price)").get()
        if not price_text:
            price_text = response.css("div.price_value::attr(data-main-price)").get()
        if price_text:
            price_clean = re.sub(r"[^\d]", "", price_text)
            item["price_usd"] = int(price_clean) if price_clean else None
        else:
            item["price_usd"] = None

        # Odometer (convert "95 тис." to 95000)
        odometer_text = response.css("div.base-information span.size18::text").get()
        if not odometer_text:
            odometer_text = response.css("span.argument::text").re_first(r"[\d\s]+тис")
        if not odometer_text:
            # Try to find in technical specifications
            odometer_text = response.xpath(
                "//div[contains(@class, 'technical-info')]//span[contains(text(), 'тис')]/text()"
            ).get()
        if odometer_text:
            # Extract number and multiply by 1000
            match = re.search(r"(\d+)", odometer_text.replace(" ", ""))
            if match:
                item["odometer"] = int(match.group(1)) * 1000
            else:
                item["odometer"] = None
        else:
            item["odometer"] = None

        # Username (seller name)
        username = response.css("div.seller_info_name a::text").get()
        if not username:
            username = response.css("h4.seller_info_name::text").get()
        if not username:
            username = response.css("div.seller_info_name::text").get()
        item["username"] = username.strip() if username else None

        # Phone number - need to click the button to reveal
        phone_number = None
        if page:
            try:
                # Try to click "show phone" button
                phone_button = await page.query_selector("a.phone_show_link, button.phones_show")
                if phone_button:
                    await phone_button.click()
                    await page.wait_for_timeout(2000)

                # Get phone number after click
                phone_elements = await page.query_selector_all(
                    "a.phone, span.phone, div.popup-phones a"
                )
                for phone_el in phone_elements:
                    phone_text = await phone_el.text_content()
                    if phone_text:
                        # Clean phone number
                        clean_phone = re.sub(r"[^\d]", "", phone_text)
                        if len(clean_phone) >= 10:
                            phone_number = int(clean_phone)
                            break
            except Exception as e:
                self.logger.warning(f"Could not get phone number: {e}")

        item["phone_number"] = phone_number

        # Image URL (main image)
        image_url = response.css("img.outline::attr(src)").get()
        if not image_url:
            image_url = response.css("div.photo-620x465 img::attr(src)").get()
        if not image_url:
            image_url = response.css("picture.picture img::attr(src)").get()
        item["image_url"] = image_url

        # Images count
        images_count_text = response.css("a.show-all span.dhide::text").get()
        if not images_count_text:
            images_count_text = response.css("span.count::text").get()
        if images_count_text:
            match = re.search(r"(\d+)", images_count_text)
            item["images_count"] = int(match.group(1)) if match else 0
        else:
            # Count gallery images
            images = response.css("div.preview-gallery img").getall()
            item["images_count"] = len(images) if images else 1

        # Car number (license plate)
        car_number = response.css("span.state-num::text").get()
        if not car_number:
            car_number = response.css("span.plate-number::text").get()
        if not car_number:
            car_number = response.xpath(
                "//span[contains(@class, 'state-num')]/text()"
            ).get()
        item["car_number"] = car_number.strip() if car_number else None

        # Car VIN
        car_vin = response.css("span.label-vin::text").get()
        if not car_vin:
            car_vin = response.css("span.vin-code::text").get()
        if not car_vin:
            # VIN might be in data attribute
            car_vin = response.css("[data-vin]::attr(data-vin)").get()
        if not car_vin:
            car_vin = response.xpath(
                "//span[contains(text(), 'VIN')]/following-sibling::span/text()"
            ).get()
        item["car_vin"] = car_vin.strip() if car_vin else None

        # Datetime found
        item["datetime_found"] = datetime.now()

        if page:
            await page.close()

        self.logger.info(f"Scraped: {item['title']} - {item['price_usd']} USD")
        yield item
