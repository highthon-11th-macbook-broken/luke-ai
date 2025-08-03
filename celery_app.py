from celery import Celery
from app.config import settings

# Celery 앱 생성
celery_app = Celery(
    "leak_detection",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=['app.tasks.detection_tasks']
)

# Celery 설정
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Asia/Seoul',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30분
    task_soft_time_limit=25 * 60,  # 25분
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# 작업 모듈 등록
celery_app.autodiscover_tasks(['app.tasks.detection_tasks']) 