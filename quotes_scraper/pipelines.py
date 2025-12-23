from itemadapter import ItemAdapter
from sqlalchemy.exc import IntegrityError
from quotes_scraper.models import Listing, get_session, init_db


class PostgresPipeline:
    def __init__(self):
        self.session = None

    def open_spider(self, spider):
        init_db()
        self.session = get_session()
        spider.logger.info("PostgreSQL connection established")

    def close_spider(self, spider):
        if self.session:
            self.session.close()
            spider.logger.info("PostgreSQL connection closed")

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        # Check if listing already exists by URL
        existing = self.session.query(Listing).filter_by(url=adapter.get("url")).first()

        if existing:
            spider.logger.info(f"Listing already exists: {adapter.get('url')}")
            return item

        listing = Listing(
            url=adapter.get("url"),
            title=adapter.get("title"),
            price_usd=adapter.get("price_usd"),
            odometer=adapter.get("odometer"),
            username=adapter.get("username"),
            phone_number=adapter.get("phone_number"),
            image_url=adapter.get("image_url"),
            images_count=adapter.get("images_count"),
            car_number=adapter.get("car_number"),
            car_vin=adapter.get("car_vin"),
            datetime_found=adapter.get("datetime_found"),
        )

        try:
            self.session.add(listing)
            self.session.commit()
            spider.logger.info(f"Saved: {adapter.get('title')}")
        except IntegrityError:
            self.session.rollback()
            spider.logger.warning(f"Duplicate entry: {adapter.get('url')}")
        except Exception as e:
            self.session.rollback()
            spider.logger.error(f"Error saving item: {e}")

        return item
