from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Team(Base):
    __tablename__ = "teams"
    
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    token = Column(String, unique=True)
    status = Column(String, default="disconnected")  # connected/disconnected
    created_at = Column(DateTime, default=datetime.utcnow)

class Task(Base):
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True)
    task_file = Column(String)
    content = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    issued_at = Column(DateTime)

class Submission(Base):
    __tablename__ = "submissions"
    
    id = Column(Integer, primary_key=True)
    team_name = Column(String, ForeignKey("teams.name"))
    task_file = Column(String)
    submission_file = Column(String)
    content = Column(JSON)
    received_at = Column(DateTime)
    submitted_at = Column(DateTime)
    processing_time = Column(Integer)  # в миллисекундах
    status = Column(String)  # SUCCESS, INVALID_JSON, INVALID_FORMAT, ERROR