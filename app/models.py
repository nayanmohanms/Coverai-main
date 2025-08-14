# app/models.py
from pydantic import BaseModel, Field
from typing import List
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

# --- Pydantic Models for the API ---
class RunRequest(BaseModel):
    """Defines the shape of the incoming request."""
    documents: str = Field(..., description="URL of the document to be processed.")
    questions: List[str] = Field(..., description="List of questions to answer about the document.")

class AnswerItem(BaseModel):
    """Defines the shape of a single question-answer pair."""
    question: str
    answer: str

class RunResponse(BaseModel):
    """Defines the shape of the final response."""
    answers: List[AnswerItem]


# --- SQLAlchemy ORM Model for the Database ---
Base = declarative_base()

class Document(Base):
    """
    Defines the 'documents' table in the database to track
    the ingestion status of files.
    """
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, index=True, unique=True)
    upload_date = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="processing") # e.g., "processing", "ready", "error"
