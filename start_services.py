#!/usr/bin/env python3
"""
서비스 실행 스크립트
FastAPI 서버와 Celery 워커를 함께 실행합니다.
"""

import subprocess
import sys
import time
import signal
import os
from pathlib import Path

def check_redis():
    """Redis 연결 확인"""
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, db=0)
        r.ping()
        print("✅ Redis 연결 확인됨")
        return True
    except Exception as e:
        print(f"❌ Redis 연결 실패: {e}")
        print("💡 Redis 서버를 먼저 실행해주세요: redis-server")
        return False

def start_celery_worker():
    """Celery 워커 시작"""
    try:
        print("🔄 Celery 워커 시작 중...")
        process = subprocess.Popen([
            sys.executable, "-m", "celery", "-A", "run_celery.celery_app", 
            "worker", "--loglevel=info"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # 워커가 시작될 때까지 잠시 대기
        time.sleep(3)
        
        if process.poll() is None:
            print("✅ Celery 워커가 성공적으로 시작됨")
            return process
        else:
            print("❌ Celery 워커 시작 실패")
            return None
    except Exception as e:
        print(f"❌ Celery 워커 시작 오류: {e}")
        return None

def start_fastapi_server():
    """FastAPI 서버 시작"""
    try:
        print("🔄 FastAPI 서버 시작 중...")
        process = subprocess.Popen([
            sys.executable, "-m", "uvicorn", "app.main:app", 
            "--reload", "--host", "0.0.0.0", "--port", "8000"
        ])
        
        print("✅ FastAPI 서버가 성공적으로 시작됨")
        print("🌐 서버 주소: http://localhost:8000")
        print("📚 API 문서: http://localhost:8000/docs")
        
        return process
    except Exception as e:
        print(f"❌ FastAPI 서버 시작 오류: {e}")
        return None

def main():
    """메인 실행 함수"""
    print("🚀 하이브리드 유출 탐지 시스템 시작")
    print("=" * 50)
    
    # Redis 확인
    if not check_redis():
        return
    
    # Celery 워커 시작
    celery_process = start_celery_worker()
    
    # FastAPI 서버 시작
    fastapi_process = start_fastapi_server()
    
    if celery_process and fastapi_process:
        print("\n🎉 모든 서비스가 성공적으로 시작되었습니다!")
        print("💡 서비스를 중지하려면 Ctrl+C를 누르세요.")
        
        try:
            # 프로세스들이 실행 중인 동안 대기
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 서비스 중지 중...")
            
            # 프로세스 종료
            if celery_process:
                celery_process.terminate()
                print("✅ Celery 워커 종료됨")
            
            if fastapi_process:
                fastapi_process.terminate()
                print("✅ FastAPI 서버 종료됨")
            
            print("👋 서비스가 안전하게 종료되었습니다.")
    else:
        print("❌ 일부 서비스 시작에 실패했습니다.")
        sys.exit(1)

if __name__ == "__main__":
    main() 