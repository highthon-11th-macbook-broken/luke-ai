from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float, Text, JSON
from sqlalchemy.sql import func
from app.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    phone = Column(String, index=True)
    name = Column(String, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class DetectionRequest(Base):
    __tablename__ = "detection_requests"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    target_email = Column(String, index=True)
    target_phone = Column(String, index=True)
    target_name = Column(String, index=True)
    status = Column(String, default="pending")  # pending, processing, completed, failed
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))

class DetectionResult(Base):
    __tablename__ = "detection_results"
    
    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(Integer, index=True)
    detection_type = Column(String)  # static_db, osint_crawl
    target_value = Column(String)
    is_leaked = Column(Boolean, default=False)
    risk_score = Column(Float, default=0.0)
    evidence = Column(Text)
    source_url = Column(String)
    detected_at = Column(DateTime(timezone=True), server_default=func.now())

class UnsolvedCase(Base):
    __tablename__ = "unsolved_cases"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    detection_result_id = Column(Integer, index=True)
    case_type = Column(String)  # high_risk, confirmed_leak
    description = Column(Text)
    evidence_data = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    resolved_at = Column(DateTime(timezone=True))
    is_resolved = Column(Boolean, default=False) 