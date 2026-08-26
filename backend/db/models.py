from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text
from backend.db.session import Base

class SubmissionCache(Base):
    __tablename__ = "submissions_cache"
    
    input_hash = Column(String(64), primary_key=True, index=True)  # SHA256 hash
    timestamp = Column(DateTime, default=datetime.utcnow)
    resume_filename = Column(String(255), nullable=True)
    result_json = Column(Text, nullable=False)  # Stores consolidated JSON string
