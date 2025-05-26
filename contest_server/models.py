from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Team(Base):
    __tablename__ = "teams"
    name = Column(String, primary_key=True)
    token = Column(String)

class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True)
    filename = Column(String)
    issued_at = Column(DateTime)

class Submission(Base):
    __tablename__ = "submissions"
    id = Column(Integer, primary_key=True, autoincrement=True)
    team_name = Column(String, ForeignKey("teams.name"))
    task_file = Column(String)
    submission_file = Column(String)
    received_at = Column(DateTime)
    submitted_at = Column(DateTime)
    processing_time = Column(Integer)  # в миллисекундах
    status = Column(String)  # SUCCESS, ERROR, etc.