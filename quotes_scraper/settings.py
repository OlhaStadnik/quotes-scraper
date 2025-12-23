# Scrapy settings for quotes_scraper project
import os
from dotenv import load_dotenv

load_dotenv()

BOT_NAME = "quotes_scraper"

SPIDER_MODULES = ["quotes_scraper.spiders"]
NEWSPIDER_MODULE = "quotes_scraper.spiders"

# Playwright settings
DOWNLOAD_HANDLERS = {
    "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
    "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
}

TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"

PLAYWRIGHT_BROWSER_TYPE = "chromium"
PLAYWRIGHT_LAUNCH_OPTIONS = {
    "headless": True,
}

# Crawl responsibly
ROBOTSTXT_OBEY = False  # AutoRia blocks bots, need to disable

# Concurrency settings for performance
CONCURRENT_REQUESTS = 8
CONCURRENT_REQUESTS_PER_DOMAIN = 4
DOWNLOAD_DELAY = 0.5

# Retry settings
RETRY_ENABLED = True
RETRY_TIMES = 3
RETRY_HTTP_CODES = [500, 502, 503, 504, 408, 429]

# User agent rotation
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

# Disable cookies to avoid tracking
COOKIES_ENABLED = False

# Configure item pipelines
ITEM_PIPELINES = {
    "quotes_scraper.pipelines.PostgresPipeline": 300,
}

# Logging
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s [%(name)s] %(levelname)s: %(message)s"

# Feed export encoding
FEED_EXPORT_ENCODING = "utf-8"

# Disable FeedExport to avoid lzma issue
EXTENSIONS = {
    "scrapy.extensions.feedexport.FeedExporter": None,
}
