from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Team(Base):
    __tablename__ = "teams"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    token = Column(String)
    last_seen = Column(DateTime, default=datetime.utcnow)

class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True)
    filename = Column(String)
    issued_at = Column(DateTime)

class Submission(Base):
    __tablename__ = "submissions"
    id = Column(Integer, primary_key=True)
    team_name = Column(String)
    task_file = Column(String)
    submission_file = Column(String)
    received_at = Column(DateTime)
