from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
import asyncio
import threading

from app.database import get_db
from app.schemas import DetectionRequestSchema, DetectionRequestResponseSchema, DetectionSummarySchema
from app.services.detection_service import DetectionService
from app.models import DetectionRequest, DetectionResult
from app.tasks.detection_tasks import run_detection_task

router = APIRouter(prefix="/detection", tags=["detection"])

# 전역 서비스 인스턴스 (실제로는 DI 컨테이너 사용 권장)
detection_service = DetectionService()

@router.post("/detect", response_model=DetectionRequestResponseSchema)
async def create_detection_request(
    request: DetectionRequestSchema,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """탐지 요청 생성"""
    
    # 임시 사용자 ID (실제로는 인증 시스템 필요)
    user_id = 1
    
    # 최소 하나의 탐지 대상이 있어야 함
    if not any([request.email, request.phone, request.name]):
        raise HTTPException(status_code=400, detail="최소 하나의 탐지 대상이 필요합니다.")
    
    try:
        # 탐지 요청 생성
        detection_request = DetectionRequest(
            user_id=user_id,
            target_email=request.email,
            target_phone=request.phone,
            target_name=request.name,
            status="pending"
        )
        db.add(detection_request)
        db.commit()
        db.refresh(detection_request)
        
        # Celery를 사용하여 백그라운드에서 탐지 수행
        try:
            run_detection_task.delay(
                user_id=user_id,
                request_id=detection_request.id,
                email=request.email,
                phone=request.phone,
                name=request.name
            )
            print(f"✅ Celery 작업이 성공적으로 큐에 추가됨: Request ID {detection_request.id}")
        except Exception as celery_error:
            print(f"⚠️ Celery 작업 큐 추가 실패: {celery_error}")
            print("🔄 백그라운드 작업으로 대체 실행...")
            
            # Celery가 실패하면 백그라운드 작업으로 대체
            background_tasks.add_task(
                perform_detection_background_fallback,
                detection_request.id,
                user_id,
                request.email,
                request.phone,
                request.name
            )
        
        return DetectionRequestResponseSchema(
            id=detection_request.id,
            user_id=detection_request.user_id,
            target_email=detection_request.target_email,
            target_phone=detection_request.target_phone,
            target_name=detection_request.target_name,
            status=detection_request.status,
            created_at=detection_request.created_at,
            completed_at=detection_request.completed_at,
            results=[]
        )
        
    except Exception as e:
        print(f"❌ 탐지 요청 생성 실패: {e}")
        raise HTTPException(status_code=500, detail=f"탐지 요청 생성 실패: {str(e)}")

def perform_detection_background_fallback(
    request_id: int,
    user_id: int,
    email: str = None,
    phone: str = None,
    name: str = None
):
    """Celery 실패 시 백그라운드에서 탐지 수행 (대체 함수)"""
    try:
        print(f"🔄 백그라운드 탐지 시작: Request ID {request_id}")
        
        # 새로운 데이터베이스 세션 생성
        from app.database import SessionLocal
        db = SessionLocal()
        
        try:
            # 요청 상태를 processing으로 업데이트
            detection_request = db.query(DetectionRequest).filter(
                DetectionRequest.id == request_id
            ).first()
            
            if detection_request:
                detection_request.status = "processing"
                db.commit()
            
            # 탐지 수행
            detection_service.perform_detection_sync(
                db=db,
                user_id=user_id,
                request_id=request_id,
                email=email,
                phone=phone,
                name=name
            )
            
            print(f"✅ 백그라운드 탐지 완료: Request ID {request_id}")
            
        finally:
            db.close()
            
    except Exception as e:
        print(f"❌ 백그라운드 탐지 실패: {e}")
        # 오류 발생 시 상태를 failed로 업데이트
        try:
            db = SessionLocal()
            detection_request = db.query(DetectionRequest).filter(
                DetectionRequest.id == request_id
            ).first()
            
            if detection_request:
                detection_request.status = "failed"
                db.commit()
            db.close()
        except:
            pass

@router.get("/requests/{request_id}", response_model=DetectionRequestResponseSchema)
async def get_detection_request(request_id: int, db: Session = Depends(get_db)):
    """탐지 요청 조회"""
    
    detection_request = db.query(DetectionRequest).filter(
        DetectionRequest.id == request_id
    ).first()
    
    if not detection_request:
        raise HTTPException(status_code=404, detail="탐지 요청을 찾을 수 없습니다.")
    
    # 결과 조회
    results = db.query(DetectionResult).filter(
        DetectionResult.request_id == request_id
    ).all()
    
    return DetectionRequestResponseSchema(
        id=detection_request.id,
        user_id=detection_request.user_id,
        target_email=detection_request.target_email,
        target_phone=detection_request.target_phone,
        target_name=detection_request.target_name,
        status=detection_request.status,
        created_at=detection_request.created_at,
        completed_at=detection_request.completed_at,
        results=results
    )

@router.get("/requests", response_model=List[DetectionRequestResponseSchema])
async def list_detection_requests(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """탐지 요청 목록 조회"""
    
    # 임시 사용자 ID
    user_id = 1
    
    detection_requests = db.query(DetectionRequest).filter(
        DetectionRequest.user_id == user_id
    ).offset(skip).limit(limit).all()
    
    results = []
    for request in detection_requests:
        # 각 요청의 결과 조회
        request_results = db.query(DetectionResult).filter(
            DetectionResult.request_id == request.id
        ).all()
        
        results.append(DetectionRequestResponseSchema(
            id=request.id,
            user_id=request.user_id,
            target_email=request.target_email,
            target_phone=request.target_phone,
            target_name=request.target_name,
            status=request.status,
            created_at=request.created_at,
            completed_at=request.completed_at,
            results=request_results
        ))
    
    return results

@router.get("/summary", response_model=DetectionSummarySchema)
async def get_detection_summary(db: Session = Depends(get_db)):
    """탐지 요약 정보 조회"""
    
    # 임시 사용자 ID
    user_id = 1
    
    summary = detection_service.get_detection_summary(db, user_id)
    
    return DetectionSummarySchema(**summary)

@router.post("/load-database")
async def load_leak_database(leak_data: dict):
    """유출 데이터베이스 로드 (관리자용)"""
    try:
        detection_service.load_leak_database(leak_data)
        return {"message": "유출 데이터베이스 로드 완료"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"데이터베이스 로드 실패: {str(e)}") 