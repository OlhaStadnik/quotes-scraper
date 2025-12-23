import os
import subprocess
import logging
from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from dotenv import load_dotenv

from db_dump import create_dump
from quotes_scraper.models import init_db

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)
logger = logging.getLogger(__name__)


def run_scraper():
    """Run the AutoRia scraper."""
    logger.info("Starting AutoRia scraper...")
    start_url = os.getenv("START_URL", "https://auto.ria.com/uk/car/used/")

    try:
        result = subprocess.run(
            ["scrapy", "crawl", "autoria", "-a", f"start_url={start_url}"],
            cwd=os.path.dirname(os.path.abspath(__file__)),
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            logger.info("Scraper completed successfully")
        else:
            logger.error(f"Scraper failed: {result.stderr}")
    except Exception as e:
        logger.error(f"Error running scraper: {e}")


def run_dump():
    """Run database dump."""
    logger.info("Starting database dump...")
    dump_file = create_dump()
    if dump_file:
        logger.info(f"Dump completed: {dump_file}")
    else:
        logger.error("Dump failed")


def parse_time(time_str):
    """Parse time string (HH:MM) to hour and minute."""
    parts = time_str.split(":")
    return int(parts[0]), int(parts[1])


def main():
    # Initialize database
    logger.info("Initializing database...")
    init_db()

    # Get schedule times from environment
    scrape_time = os.getenv("SCRAPE_TIME", "12:00")
    dump_time = os.getenv("DUMP_TIME", "12:00")

    scrape_hour, scrape_minute = parse_time(scrape_time)
    dump_hour, dump_minute = parse_time(dump_time)

    # Create scheduler
    scheduler = BlockingScheduler()

    # Schedule scraper job
    scheduler.add_job(
        run_scraper,
        CronTrigger(hour=scrape_hour, minute=scrape_minute),
        id="scraper_job",
        name="AutoRia Scraper",
        replace_existing=True,
    )
    logger.info(f"Scraper scheduled to run daily at {scrape_time}")

    # Schedule dump job
    scheduler.add_job(
        run_dump,
        CronTrigger(hour=dump_hour, minute=dump_minute),
        id="dump_job",
        name="Database Dump",
        replace_existing=True,
    )
    logger.info(f"Database dump scheduled to run daily at {dump_time}")

    # Run initial scrape and dump on startup (optional)
    run_once = os.getenv("RUN_ON_STARTUP", "false").lower() == "true"
    if run_once:
        logger.info("Running initial scrape...")
        run_scraper()
        run_dump()

    logger.info("Scheduler started. Press Ctrl+C to exit.")
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Scheduler stopped.")


if __name__ == "__main__":
    main()
