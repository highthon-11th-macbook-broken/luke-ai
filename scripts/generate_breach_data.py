#!/usr/bin/env python3
"""
유출 DB용 샘플 데이터 생성 스크립트
"""

import sys
import os
import json
from faker import Faker
import random

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 한국어 기반 Faker
fake = Faker('ko_KR')

def generate_password_patterns():
    """비밀번호 패턴 생성"""
    patterns = [
        "qwerty123", "pass1234", "sunny97!", "1234lee",
        "mk8908@!", "choi!pw", "hello2020", "test@321",
        "abc123!", "mypw!456", "pw123456", "1q2w3e4r",
        "password123", "123456", "qwerty", "admin123",
        "letmein", "welcome", "monkey", "dragon",
        "master", "football", "baseball", "shadow"
    ]
    return random.sample(patterns, k=random.randint(2, 4))

def create_breach_database(num_samples=1000):
    """유출 데이터베이스 생성"""
    
    print(f"🔧 {num_samples}개의 유출 데이터 생성 중...")
    
    # 데이터 수집용 딕셔너리
    breach_data = {
        'emails': [],
        'phones': [],
        'names': [],
        'passwords': []
    }
    
    for i in range(num_samples):
        # 기본 정보 생성
        name = fake.name()
        email = fake.email()
        phone = fake.phone_number()
        
        # 비밀번호 패턴 생성
        password_patterns = generate_password_patterns()
        
        # 데이터 추가
        breach_data['emails'].append(email)
        breach_data['phones'].append(phone)
        breach_data['names'].append(name)
        breach_data['passwords'].extend(password_patterns)
        
        # 진행률 표시
        if (i + 1) % 100 == 0:
            print(f"   {i + 1}/{num_samples} 완료...")
    
    # 중복 제거
    breach_data['emails'] = list(set(breach_data['emails']))
    breach_data['phones'] = list(set(breach_data['phones']))
    breach_data['names'] = list(set(breach_data['names']))
    breach_data['passwords'] = list(set(breach_data['passwords']))
    
    print(f"✅ 유출 데이터 생성 완료!")
    print(f"   📧 이메일: {len(breach_data['emails'])}개")
    print(f"   📞 전화번호: {len(breach_data['phones'])}개")
    print(f"   👤 이름: {len(breach_data['names'])}개")
    print(f"   🔑 비밀번호 패턴: {len(breach_data['passwords'])}개")
    
    return breach_data

def save_breach_data(breach_data, filename="breach_database.json"):
    """유출 데이터를 JSON 파일로 저장"""
    
    filepath = os.path.join(os.path.dirname(__file__), filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(breach_data, f, ensure_ascii=False, indent=2)
    
    print(f"💾 유출 데이터 저장 완료: {filepath}")
    return filepath

def load_breach_data_to_system(force_regenerate=False):
    """생성된 유출 데이터를 시스템에 로드"""
    
    filepath = os.path.join(os.path.dirname(__file__), "breach_database.json")
    
    # 기존 데이터 파일이 있고 강제 재생성이 아닌 경우
    if os.path.exists(filepath) and not force_regenerate:
        try:
            print("📂 기존 유출 데이터 파일을 로드합니다...")
            with open(filepath, 'r', encoding='utf-8') as f:
                breach_data = json.load(f)
            
            print(f"✅ 기존 유출 데이터 로드 완료!")
            print(f"   📧 이메일: {len(breach_data['emails'])}개")
            print(f"   📞 전화번호: {len(breach_data['phones'])}개")
            print(f"   👤 이름: {len(breach_data['names'])}개")
            print(f"   🔑 비밀번호 패턴: {len(breach_data['passwords'])}개")
            
            return breach_data
            
        except Exception as e:
            print(f"⚠️ 기존 데이터 로드 실패: {e}")
            print("🔄 새로운 데이터를 생성합니다...")
    
    # 새로운 데이터 생성
    try:
        print("🔄 새로운 유출 데이터를 생성합니다...")
        
        # 유출 데이터 생성
        breach_data = create_breach_database(1000)
        
        # 파일로 저장
        save_breach_data(breach_data)
        
        print("✅ 유출 데이터가 시스템에 로드되었습니다!")
        
        return breach_data
        
    except Exception as e:
        print(f"❌ 유출 데이터 로드 실패: {e}")
        return None

if __name__ == "__main__":
    # 유출 데이터 생성 및 시스템 로드
    breach_data = load_breach_data_to_system()
    
    if breach_data:
        print("\n🎯 테스트용 샘플 데이터:")
        print(f"   이메일: {breach_data['emails'][0]}")
        print(f"   전화번호: {breach_data['phones'][0]}")
        print(f"   이름: {breach_data['names'][0]}")
        print(f"   비밀번호 패턴: {breach_data['passwords'][:3]}")
        
        print("\n💡 이제 이 데이터로 탐지 테스트를 할 수 있습니다!") 