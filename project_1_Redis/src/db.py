from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime

DATABASE_URL = "sqlite:///meetings.db"  # or use PostgreSQL with proper URI
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = 'user'
    email = Column(String, primary_key=True, index=True)
    name = Column(String)
    age = Column(Integer)
    gender = Column(String)

class Meeting(Base):
    __tablename__ = 'meeting'
    meetingID = Column(String, primary_key=True, index=True)
    title = Column(String)
    description = Column(Text)
    t1 = Column(DateTime)
    t2 = Column(DateTime)
    lat = Column(Float)
    long = Column(Float)
    participants = Column(Text)  # Comma-separated emails

class Log(Base):
    __tablename__ = 'log'
    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String, ForeignKey("user.email"))
    meetingID = Column(String, ForeignKey("meeting.meetingID"))
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    action = Column(Integer)  # 1 = join, 2 = leave, 3 = time_out

def init_db():
    Base.metadata.create_all(bind=engine)
