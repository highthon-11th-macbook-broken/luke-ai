#!/usr/bin/env python3
"""
전체 탐지 시스템 테스트 스크립트
"""

import asyncio
import sys
import os
from dotenv import load_dotenv

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.detection_service import DetectionService
from app.database import SessionLocal
from scripts.generate_breach_data import create_breach_database

async def test_detection_system():
    """전체 탐지 시스템 테스트"""
    
    # 환경 변수 로드
    load_dotenv()
    
    try:
        print("🔧 탐지 시스템 테스트 시작...")
        
        # 1. 유출 데이터 생성
        print("\n📊 1. 유출 데이터 생성 중...")
        breach_data = create_breach_database(500)  # 500개 샘플
        
        # 2. 탐지 서비스 초기화
        print("\n⚙️ 2. 탐지 서비스 초기화 중...")
        detection_service = DetectionService()
        detection_service.load_leak_database(breach_data)
        
        # 3. 데이터베이스 세션 생성
        print("\n🗄️ 3. 데이터베이스 연결 중...")
        db = SessionLocal()
        
        # 4. 탐지 테스트
        print("\n🔍 4. 탐지 테스트 수행 중...")
        
        # 테스트 케이스들
        test_cases = [
            {
                'email': breach_data['emails'][0],  # 유출된 이메일
                'phone': breach_data['phones'][0],   # 유출된 전화번호
                'name': breach_data['names'][0]      # 유출된 이름
            },
            {
                'email': 'not_leaked@example.com',  # 유출되지 않은 이메일
                'phone': '010-9999-9999',           # 유출되지 않은 전화번호
                'name': '김테스트'                    # 유출되지 않은 이름
            }
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n🧪 테스트 케이스 {i}:")
            print(f"   이메일: {test_case['email']}")
            print(f"   전화번호: {test_case['phone']}")
            print(f"   이름: {test_case['name']}")
            
            # 탐지 수행
            result = await detection_service.perform_detection(
                db=db,
                user_id=1,
                email=test_case['email'],
                phone=test_case['phone'],
                name=test_case['name']
            )
            
            print(f"   결과: {result}")
        
        # 5. 요약 정보 조회
        print("\n📈 5. 탐지 요약 정보:")
        summary = detection_service.get_detection_summary(db, 1)
        print(f"   총 요청 수: {summary['total_requests']}")
        print(f"   완료된 요청 수: {summary['completed_requests']}")
        print(f"   유출된 정보 수: {summary['leaked_count']}")
        print(f"   고위험 정보 수: {summary['high_risk_count']}")
        print(f"   미제사건 수: {summary['unsolved_cases']}")
        
        db.close()
        
        print("\n✅ 탐지 시스템 테스트 완료!")
        
    except Exception as e:
        print(f"❌ 탐지 시스템 테스트 실패: {e}")
        print("\n🔧 확인사항:")
        print("1. 데이터베이스가 실행 중인지 확인")
        print("2. Redis가 실행 중인지 확인")
        print("3. .env 파일의 설정이 올바른지 확인")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(test_detection_system()) 