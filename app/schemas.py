from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

# 요청 스키마
class DetectionRequestSchema(BaseModel):
    email: Optional[str] = None
    phone: Optional[str] = None
    name: Optional[str] = None

class UserCreateSchema(BaseModel):
    email: EmailStr
    phone: Optional[str] = None
    name: Optional[str] = None

# 응답 스키마
class DetectionResultSchema(BaseModel):
    id: int
    request_id: int
    detection_type: str
    target_value: str
    is_leaked: bool
    risk_score: float
    evidence: Optional[str] = None
    source_url: Optional[str] = None
    detected_at: datetime

    class Config:
        from_attributes = True

class DetectionRequestResponseSchema(BaseModel):
    id: int
    user_id: int
    target_email: Optional[str] = None
    target_phone: Optional[str] = None
    target_name: Optional[str] = None
    status: str
    created_at: datetime
    completed_at: Optional[datetime] = None
    results: List[DetectionResultSchema] = []

    class Config:
        from_attributes = True

class UnsolvedCaseSchema(BaseModel):
    id: int
    user_id: int
    detection_result_id: int
    case_type: str
    description: str
    evidence_data: dict
    created_at: datetime
    resolved_at: Optional[datetime] = None
    is_resolved: bool

    class Config:
        from_attributes = True

class DetectionSummarySchema(BaseModel):
    total_requests: int
    completed_requests: int
    leaked_count: int
    high_risk_count: int
    unsolved_cases: int 