from app.services.detection_service import DetectionService
from app.database import SessionLocal
from celery_app import celery_app
import asyncio

detection_service = DetectionService()

@celery_app.task(bind=True)
def run_detection_task(self, user_id: int, request_id: int, email: str = None, phone: str = None, name: str = None):
    """백그라운드에서 탐지 작업 수행"""
    
    # 작업 상태 업데이트
    self.update_state(
        state='PROGRESS',
        meta={'current': 0, 'total': 4, 'status': '탐지 시작'}
    )
    
    try:
        # 데이터베이스 세션 생성
        db = SessionLocal()
        
        try:
            # 요청 상태를 processing으로 업데이트
            from app.models import DetectionRequest
            detection_request = db.query(DetectionRequest).filter(
                DetectionRequest.id == request_id
            ).first()
            
            if detection_request:
                detection_request.status = "processing"
                db.commit()
            
            # 탐지 수행 (동기 버전 사용)
            result = detection_service.perform_detection_sync(
                db=db,
                user_id=user_id,
                request_id=request_id,
                email=email,
                phone=phone,
                name=name
            )
            
            # 작업 완료 상태 업데이트
            self.update_state(
                state='SUCCESS',
                meta={
                    'current': 4,
                    'total': 4,
                    'status': '탐지 완료',
                    'result': result
                }
            )
            
            return result
            
        finally:
            db.close()
            
    except Exception as e:
        # 오류 상태 업데이트
        self.update_state(
            state='FAILURE',
            meta={
                'current': 0,
                'total': 4,
                'status': f'탐지 실패: {str(e)}'
            }
        )
        
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
        
        raise e

@celery_app.task
def monitor_ongoing_leaks():
    """지속적인 유출 모니터링 작업"""
    # 24시간 자동 모니터링 로직
    # 실제 구현에서는 스케줄러와 연동
    pass 