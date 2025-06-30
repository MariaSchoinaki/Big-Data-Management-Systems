from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timezone

DATABASE_URL = "sqlite:///meetings.db"
engine = create_engine(DATABASE_URL, echo=False, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

class User(Base):
    __tablename__ = 'user'
    email   = Column(String, primary_key=True, index=True)
    name    = Column(String, nullable=False)
    age     = Column(Integer)
    gender  = Column(String)

class Meeting(Base):
    __tablename__ = 'meeting'
    meetingID    = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title        = Column(String, nullable=False)
    description  = Column(Text)
    t1           = Column(DateTime(timezone=True), nullable=False)
    t2           = Column(DateTime(timezone=True), nullable=False)
    lat          = Column(Float, nullable=False)
    long         = Column(Float, nullable=False)
    participants = Column(Text, default="")  # CSV of emails  # Comma-separated emails

class Log(Base):
    __tablename__ = 'log'
    id         = Column(Integer, primary_key=True, autoincrement=True)
    email      = Column(String, ForeignKey("user.email"), nullable=False)
    meetingID  = Column(Integer, ForeignKey("meeting.meetingID"), nullable=False)
    timestamp  = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)
    action     = Column(Integer, nullable=False)  # 1 = join, 2 = leave, 3 = time_out

def init_db():
    """
    Create all tables. Safe to call on every startup.
    """
    Base.metadata.create_all(bind=engine)