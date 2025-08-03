from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.api.detection import router as detection_router
from app.database import get_db, engine
from app.models import Base
from app.services.detection_service import DetectionService

# 데이터베이스 테이블 생성
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="하이브리드 유출 탐지 시스템",
    description="정적 DB 탐지와 OSINT 크롤링을 통합한 개인정보 유출 탐지 시스템",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 정적 파일 서빙
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# 템플릿 설정
templates = Jinja2Templates(directory="app/templates")

# 라우터 등록
app.include_router(detection_router)

@app.get("/")
async def root():
    return {
        "message": "하이브리드 유출 탐지 시스템 API",
        "version": "1.0.0",
        "endpoints": {
            "detection": "/detection",
            "docs": "/docs",
            "dashboard": "/dashboard"
        }
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/dashboard")
async def dashboard(request: Request, db: Session = Depends(get_db)):
    """웹 대시보드"""
    detection_service = DetectionService()
    
    # 임시 사용자 ID
    user_id = 1
    
    # 탐지 요약 정보 가져오기
    try:
        summary = detection_service.get_detection_summary(db, user_id)
    except Exception as e:
        # 오류 발생 시 기본값 사용
        summary = {
            'total_requests': 0,
            'completed_requests': 0,
            'leaked_count': 0,
            'high_risk_count': 0,
            'unsolved_cases': 0
        }
    
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "summary": summary
    }) 