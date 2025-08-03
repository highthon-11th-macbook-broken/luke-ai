#!/usr/bin/env python3
"""
샘플 유출 데이터 로드 스크립트
Faker를 사용하여 현실적인 유출 데이터를 생성합니다.
"""

import sys
import os

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.generate_breach_data import load_breach_data_to_system

def load_sample_data():
    """샘플 유출 데이터 로드"""
    
    try:
        print("🔧 유출 데이터 생성 및 로드 중...")
        
        # 유출 데이터 생성 및 시스템 로드
        breach_data = load_breach_data_to_system()
        
        if breach_data:
            print("✅ 유출 데이터 로드 완료!")
            print("\n🎯 테스트용 샘플 데이터:")
            print(f"   이메일: {breach_data['emails'][0]}")
            print(f"   전화번호: {breach_data['phones'][0]}")
            print(f"   이름: {breach_data['names'][0]}")
            print(f"   비밀번호 패턴: {breach_data['passwords'][:3]}")
            
            print("\n💡 이제 이 데이터로 탐지 테스트를 할 수 있습니다!")
        else:
            print("❌ 유출 데이터 로드 실패")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ 샘플 데이터 로드 실패: {e}")
        sys.exit(1)

if __name__ == "__main__":
    load_sample_data() 