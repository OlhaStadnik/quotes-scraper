# AutoRia Scraper

Scraper for collecting used car listings from AutoRia.com.ua with scheduled daily runs and PostgreSQL storage.

## Features

- Scrapes all car listing fields (url, title, price, odometer, seller info, images, VIN, etc.)
- PostgreSQL database storage with duplicate prevention
- Daily scheduled scraping at configurable time
- Daily database dumps
- Docker deployment
- Playwright for JavaScript-rendered content (phone numbers)

## Project Structure

```
quotes-scraper/
├── quotes_scraper/
│   ├── __init__.py
│   ├── items.py           # Scrapy item definitions
│   ├── models.py          # SQLAlchemy database models
│   ├── pipelines.py       # PostgreSQL pipeline
│   ├── settings.py        # Scrapy settings
│   ├── middlewares.py     # Scrapy middlewares
│   └── spiders/
│       ├── __init__.py
│       └── autoria.py     # Main spider
├── main.py                # Entry point with scheduler
├── db_dump.py             # Database dump utility
├── scrapy.cfg             # Scrapy configuration
├── requirements.txt       # Python dependencies
├── Dockerfile
├── docker-compose.yml
├── .env                   # Environment configuration
├── .env.example           # Example configuration
└── dumps/                 # Database dumps directory
```

## Database Fields

| Field | Type | Description |
|-------|------|-------------|
| url | String | Listing URL |
| title | String | Car title |
| price_usd | Integer | Price in USD |
| odometer | Integer | Mileage in km (e.g., 95000) |
| username | String | Seller name |
| phone_number | BigInteger | Phone number (e.g., 380631234567) |
| image_url | String | Main image URL |
| images_count | Integer | Total images count |
| car_number | String | License plate |
| car_vin | String | VIN code |
| datetime_found | DateTime | When the listing was scraped |

## Quick Start

### Using Docker (Recommended)

1. Clone the repository:
```bash
git clone <repository-url>
cd quotes-scraper
```

2. Copy and configure environment:
```bash
cp .env.example .env
# Edit .env with your settings
```

3. Start the application:
```bash
docker-compose up -d
```

4. View logs:
```bash
docker-compose logs -f scraper
```

### Local Development

1. Install dependencies:
```bash
pip install -r requirements.txt
playwright install chromium
```

2. Start PostgreSQL (or use Docker):
```bash
docker run -d --name postgres -e POSTGRES_DB=autoria -e POSTGRES_PASSWORD=postgres -p 5432:5432 postgres:15-alpine
```

3. Configure environment:
```bash
cp .env.example .env
# Edit .env with your settings
```

4. Run the scheduler:
```bash
python main.py
```

Or run the spider directly:
```bash
scrapy crawl autoria
```

## Configuration

Environment variables (`.env` file):

| Variable | Default | Description |
|----------|---------|-------------|
| POSTGRES_HOST | localhost | Database host |
| POSTGRES_PORT | 5432 | Database port |
| POSTGRES_DB | autoria | Database name |
| POSTGRES_USER | postgres | Database user |
| POSTGRES_PASSWORD | postgres | Database password |
| START_URL | https://auto.ria.com/uk/car/used/ | Starting URL for scraping |
| SCRAPE_TIME | 12:00 | Daily scrape time (HH:MM) |
| DUMP_TIME | 12:00 | Daily dump time (HH:MM) |
| DUMPS_DIR | dumps | Directory for database dumps |
| RUN_ON_STARTUP | false | Run scraper immediately on startup |

## Manual Database Dump

```bash
python db_dump.py
```

Dumps are saved to the `dumps/` directory with timestamp in filename.

## Stopping the Application

```bash
docker-compose down
```

To also remove database data:
```bash
docker-compose down -v
```
