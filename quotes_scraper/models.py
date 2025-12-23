import os
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, BigInteger, String, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv()

Base = declarative_base()


class Listing(Base):
    __tablename__ = "listings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(String(500), unique=True, nullable=False)
    title = Column(String(500))
    price_usd = Column(Integer)
    odometer = Column(Integer)
    username = Column(String(255))
    phone_number = Column(BigInteger)
    image_url = Column(String(500))
    images_count = Column(Integer)
    car_number = Column(String(50))
    car_vin = Column(String(50))
    datetime_found = Column(DateTime, default=datetime.now)

    def __repr__(self):
        return f"<Listing(id={self.id}, title='{self.title}', price={self.price_usd})>"


def get_database_url():
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = os.getenv("POSTGRES_PORT", "5432")
    db = os.getenv("POSTGRES_DB", "autoria")
    user = os.getenv("POSTGRES_USER", "postgres")
    password = os.getenv("POSTGRES_PASSWORD", "postgres")
    return f"postgresql://{user}:{password}@{host}:{port}/{db}"


def get_engine():
    return create_engine(get_database_url())


def get_session():
    engine = get_engine()
    Session = sessionmaker(bind=engine)
    return Session()


def init_db():
    engine = get_engine()
    Base.metadata.create_all(engine)
    return engine
