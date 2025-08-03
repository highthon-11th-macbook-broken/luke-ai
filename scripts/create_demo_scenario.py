#!/usr/bin/env python3
"""
해커톤 데모용 현실적인 유출 시나리오 생성 스크립트
사용자가 입력한 정보가 "발견"되도록 미리 준비된 데이터셋 생성
"""

import os
import sys
import json
import hashlib
import random
from datetime import datetime, timedelta

# 프로젝트 루트 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.demo_data_generator import DemoDataGenerator
from faker import Faker

class DemoScenarioCreator:
    """데모 시나리오 생성기"""
    
    def __init__(self):
        self.fake = Faker(['ko_KR', 'en_US'])
        self.demo_generator = DemoDataGenerator()
        
        # 해커톤에서 사용할 테스트 계정들
        self.demo_accounts = [
            {
                "email": "demo@hackathon.com",
                "phone": "010-1234-5678",
                "name": "김해커",
                "scenario": "high_risk_victim"
            },
            {
                "email": "test.user@example.com", 
                "phone": "010-9876-5432",
                "name": "이테스트",
                "scenario": "medium_risk_exposure"
            },
            {
                "email": "secure.person@safe.co.kr",
                "phone": "010-1111-2222", 
                "name": "박안전",
                "scenario": "low_risk_clean"
            },
            {
                "email": "victim@breached.org",
                "phone": "010-5555-7777",
                "name": "최피해",
                "scenario": "critical_breach"
            }
        ]
    
    def create_comprehensive_demo_data(self):
        """종합적인 데모 데이터 생성"""
        
        print("🎭 해커톤 데모 시나리오 생성 시작...")
        
        # 1. 정적 DB용 유출 데이터 생성
        static_leak_data = self._create_static_leak_data()
        
        # 2. OSINT 크롤링 결과 시뮬레이션 데이터 생성
        osint_scenarios = self._create_osint_scenarios()
        
        # 3. AI 분석 결과 템플릿 생성
        ai_analysis_templates = self._create_ai_templates()
        
        # 4. 파일로 저장
        self._save_demo_data({
            'static_leaks': static_leak_data,
            'osint_scenarios': osint_scenarios,
            'ai_templates': ai_analysis_templates,
            'demo_accounts': self.demo_accounts,
            'creation_timestamp': datetime.now().isoformat()
        })
        
        print("✅ 데모 시나리오 생성 완료!")
        self._print_demo_guide()
    
    def _create_static_leak_data(self) -> dict:
        """정적 DB용 데이터 생성"""
        
        print("📊 정적 유출 데이터 생성 중...")
        
        static_data = {
            'emails': [],
            'phones': [],
            'names': [],
            'passwords': []
        }
        
        # 데모 계정들을 포함하도록 설정
        for account in self.demo_accounts:
            if account['scenario'] in ['high_risk_victim', 'critical_breach', 'medium_risk_exposure']:
                static_data['emails'].append(account['email'])
                static_data['phones'].append(account['phone'])
                static_data['names'].append(account['name'])
        
        # 추가 랜덤 데이터 생성
        for _ in range(10000):  # 충분한 배경 데이터
            static_data['emails'].append(self.fake.email())
            static_data['phones'].append(self.fake.phone_number())
            static_data['names'].append(self.fake.name())
        
        # 패스워드 패턴 추가
        common_passwords = [
            'password123', '123456789', 'qwerty123', 'admin123',
            'password1', 'welcome123', 'test1234', 'user12345'
        ]
        static_data['passwords'].extend(common_passwords)
        
        return static_data
    
    def _create_osint_scenarios(self) -> list:
        """OSINT 크롤링 시나리오 생성"""
        
        print("🔍 OSINT 시나리오 생성 중...")
        
        scenarios = []
        
        for account in self.demo_accounts:
            account_scenarios = self._generate_account_scenarios(account)
            scenarios.extend(account_scenarios)
        
        # 일반적인 배경 시나리오 추가
        background_scenarios = self._generate_background_scenarios(50)
        scenarios.extend(background_scenarios)
        
        return scenarios
    
    def _generate_account_scenarios(self, account: dict) -> list:
        """특정 계정의 시나리오 생성"""
        
        scenarios = []
        scenario_type = account['scenario']
        
        if scenario_type == 'critical_breach':
            # 매우 위험한 유출 시나리오
            scenarios.extend([
                {
                    'target_email': account['email'],
                    'target_phone': account['phone'],
                    'target_name': account['name'],
                    'leak_type': 'database_breach',
                    'source_url': 'https://pastebin.com/raw/XvZ9mN2k',
                    'context': f"Database dump from TechCorp breach - User ID: 156789, Email: {self._mask_email(account['email'])}, Phone: {self._mask_phone(account['phone'])}, Password: ••••••••, Registration: 2019-03-15",
                    'risk_score': 0.95,
                    'evidence': 'TechCorp 기업 데이터베이스 유출에서 발견됨',
                    'ai_reasoning': '구조화된 데이터베이스 형태의 개인정보 노출이 감지되었습니다. 비밀번호 정보가 함께 노출되어 있어 매우 위험합니다. 즉시 조치가 필요한 매우 높은 위험도입니다.'
                },
                {
                    'target_email': account['email'],
                    'target_phone': account['phone'],
                    'target_name': account['name'],
                    'leak_type': 'paste_site',
                    'source_url': 'https://pastebin.com/raw/Abc123Def',
                    'context': f"Account credentials dump: {self._mask_email(account['email'])}:••••••••:admin | Phone: {self._mask_phone(account['phone'])} | Created: 2023-08-12",
                    'risk_score': 0.92,
                    'evidence': '공개 페이스트 사이트에서 계정 정보 발견',
                    'ai_reasoning': '페이스트 사이트에 업로드된 민감한 정보가 탐지되었습니다. 비밀번호 정보가 함께 노출되어 있어 매우 위험합니다. 즉시 조치가 필요한 매우 높은 위험도입니다.'
                }
            ])
        
        elif scenario_type == 'high_risk_victim':
            scenarios.extend([
                {
                    'target_email': account['email'],
                    'target_phone': account['phone'],
                    'target_name': account['name'],
                    'leak_type': 'forum_post',
                    'source_url': 'https://reddit.com/r/DataBreach/comments/xyz123',
                    'context': f"Username: hacker_kim posting personal info - Contact: {self._mask_email(account['email'])}, Mobile: {self._mask_phone(account['phone'])}, Location: Seoul",
                    'risk_score': 0.78,
                    'evidence': '온라인 포럼에서 개인정보 공개 발견',
                    'ai_reasoning': '온라인 포럼에서 부주의한 개인정보 공개가 발견되었습니다. 이메일 주소가 명시적으로 포함되어 있습니다. 신속한 대응이 권장되는 높은 위험도입니다.'
                }
            ])
        
        elif scenario_type == 'medium_risk_exposure':
            scenarios.extend([
                {
                    'target_email': account['email'],
                    'target_phone': account['phone'],
                    'target_name': account['name'],
                    'leak_type': 'social_media',
                    'source_url': 'https://twitter.com/randomuser/status/1234567890',
                    'context': f"Social media profile leak - Name: {self._mask_name(account['name'])}, Email: {self._mask_email(account['email'])}, Phone: {self._mask_phone(account['phone'])}, DOB: 1985-07-22",
                    'risk_score': 0.62,
                    'evidence': '소셜미디어에서 개인정보 노출 확인',
                    'ai_reasoning': '소셜미디어에서 과도한 개인정보 공개가 관찰되었습니다. 주의 깊은 모니터링이 필요한 중간 위험도입니다.'
                }
            ])
        
        # scenario_type이 'low_risk_clean'인 경우는 의도적으로 시나리오를 생성하지 않음
        
        return scenarios
    
    def _generate_background_scenarios(self, count: int) -> list:
        """배경 노이즈용 시나리오 생성"""
        
        scenarios = []
        
        for _ in range(count):
            fake_email = self.fake.email()
            fake_phone = self.fake.phone_number()
            fake_name = self.fake.name()
            
            scenario = random.choice(self.demo_generator.leak_scenarios)
            
            scenarios.append({
                'target_email': fake_email,
                'target_phone': fake_phone,
                'target_name': fake_name,
                'leak_type': scenario['type'],
                'source_url': random.choice(self.demo_generator.realistic_sources),
                'context': scenario['context_template'].format(
                    company=random.choice(self.demo_generator.companies),
                    user_id=random.randint(100000, 999999),
                    email=self._mask_email(fake_email),
                    phone=self._mask_phone(fake_phone),
                    name=self._mask_name(fake_name),
                    username=fake_name.lower().replace(' ', '') + str(random.randint(10, 999)),
                    password="••••••••",
                    date=self._random_date(),
                    location=self.fake.city(),
                    dob=self.fake.date_of_birth(),
                    order_id=random.randint(10000, 99999),
                    address=self.fake.address()
                ),
                'risk_score': round(random.uniform(*scenario['risk_score_range']), 2),
                'evidence': scenario['evidence_template'].format(
                    company=random.choice(self.demo_generator.companies)
                ),
                'ai_reasoning': self._generate_background_reasoning(scenario['type'])
            })
        
        return scenarios
    
    def _create_ai_templates(self) -> dict:
        """AI 분석 템플릿 생성"""
        
        print("🤖 AI 분석 템플릿 생성 중...")
        
        return {
            'risk_level_descriptions': {
                'critical': '즉시 조치가 필요한 치명적 위험도',
                'high': '신속한 대응이 권장되는 높은 위험도',
                'medium': '주의 깊은 모니터링이 필요한 중간 위험도',
                'low': '낮은 위험도이지만 지속적인 관찰 필요'
            },
            'recommendation_templates': {
                'password_change': '즉시 해당 계정의 비밀번호를 변경하세요.',
                'two_factor': '2단계 인증을 모든 중요 계정에 설정하세요.',
                'monitoring': '정기적인 개인정보 노출 스캔을 설정하세요.',
                'report': '관련 서비스 제공업체에 유출 신고를 하세요.'
            }
        }
    
    def _save_demo_data(self, data: dict):
        """데모 데이터를 파일로 저장"""
        
        # scripts 디렉토리에 저장
        output_file = os.path.join(os.path.dirname(__file__), 'demo_scenarios.json')
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"📁 데모 데이터 저장됨: {output_file}")
        
        # 해커톤용 간단 가이드 파일도 생성
        guide_file = os.path.join(os.path.dirname(__file__), 'demo_guide.md')
        with open(guide_file, 'w', encoding='utf-8') as f:
            f.write(self._generate_demo_guide_content())
        
        print(f"📖 데모 가이드 생성됨: {guide_file}")
    
    def _generate_demo_guide_content(self) -> str:
        """데모 가이드 내용 생성"""
        
        guide_content = """# 🎭 해커톤 데모 가이드

## 📋 준비된 테스트 계정

### 1. 치명적 위험 시나리오
- **이메일**: victim@breached.org
- **전화번호**: 010-5555-7777
- **이름**: 최피해
- **예상 결과**: 매우 높은 위험도, 다중 유출 사례 발견

### 2. 높은 위험 시나리오  
- **이메일**: demo@hackathon.com
- **전화번호**: 010-1234-5678
- **이름**: 김해커
- **예상 결과**: 높은 위험도, 포럼 노출 사례

### 3. 중간 위험 시나리오
- **이메일**: test.user@example.com
- **전화번호**: 010-9876-5432
- **이름**: 이테스트
- **예상 결과**: 중간 위험도, 소셜미디어 노출

### 4. 안전한 시나리오
- **이메일**: secure.person@safe.co.kr
- **전화번호**: 010-1111-2222
- **이름**: 박안전
- **예상 결과**: 낮은 위험도, 깨끗한 상태

## 🎯 데모 시연 팁

1. **치명적 사례부터 시작**: 임팩트가 큰 결과를 먼저 보여주세요
2. **AI 분석 강조**: AI가 분석한 위험도와 권장사항을 부각하세요
3. **시각적 효과**: 대시보드의 위험도 차트와 그래프를 활용하세요
4. **실시간 느낌**: 탐지 과정을 단계별로 보여주세요

## 🔧 시스템 특징 어필 포인트

- **하이브리드 탐지**: 정적 DB + 실시간 크롤링 + AI 분석
- **빠른 응답**: 정적 DB는 50-150ms 내 응답
- **현실적 결과**: 실제 유출 사례와 유사한 패턴
- **AI 인사이트**: 단순 탐지를 넘어선 분석과 권장사항

## ⚠️ 주의사항

- 데모 데이터는 모두 가상의 정보입니다
- 실제 개인정보는 포함되지 않습니다  
- 해커톤 목적으로만 사용하세요
"""
        
        return guide_content
    
    def _mask_email(self, email: str) -> str:
        """이메일 마스킹"""
        if '@' not in email:
            return email
        local, domain = email.split('@', 1)
        if len(local) <= 2:
            return email
        return f"{local[0]}***{local[-1]}@{domain}"
    
    def _mask_phone(self, phone: str) -> str:
        """전화번호 마스킹"""
        clean_phone = ''.join(filter(str.isdigit, phone))
        if len(clean_phone) < 8:
            return phone
        return clean_phone[:3] + '****' + clean_phone[-4:]
    
    def _mask_name(self, name: str) -> str:
        """이름 마스킹"""
        if len(name) <= 2:
            return name
        return name[0] + '*' * (len(name) - 2) + name[-1]
    
    def _random_date(self) -> str:
        """무작위 날짜 생성"""
        start_date = datetime.now() - timedelta(days=365*3)
        end_date = datetime.now()
        random_date = start_date + timedelta(
            seconds=random.randint(0, int((end_date - start_date).total_seconds()))
        )
        return random_date.strftime("%Y-%m-%d")
    
    def _generate_background_reasoning(self, leak_type: str) -> str:
        """배경 시나리오용 AI 추론 생성"""
        templates = {
            'database_breach': '데이터베이스 유출 패턴과 일치하는 구조화된 개인정보가 발견되었습니다. 높은 위험도로 신속한 조치가 권장됩니다.',
            'paste_site': '페이스트 사이트에 업로드된 민감한 정보가 탐지되었습니다. 매우 높은 위험도로 즉시 대응이 필요합니다.',
            'forum_post': '온라인 포럼에서 부주의한 개인정보 공개가 발견되었습니다. 중간 위험도로 주의가 필요합니다.',
            'social_media': '소셜미디어에서 과도한 개인정보 공개가 관찰되었습니다. 낮은 위험도이지만 지속적인 관찰이 필요합니다.',
            'shopping_site': '이커머스 플랫폼 고객 데이터 유출에서 발견되었습니다. 높은 위험도로 신속한 조치가 권장됩니다.'
        }
        return templates.get(leak_type, '개인정보 유출이 탐지되었습니다. 주의가 필요합니다.')
    
    def _print_demo_guide(self):
        """데모 가이드 출력"""
        
        print("\n" + "="*60)
        print("🎭 해커톤 데모 준비 완료!")
        print("="*60)
        print("\n📋 테스트 계정 목록:")
        
        for i, account in enumerate(self.demo_accounts, 1):
            risk_level = {
                'critical_breach': '🔴 치명적 위험',
                'high_risk_victim': '🟠 높은 위험', 
                'medium_risk_exposure': '🟡 중간 위험',
                'low_risk_clean': '🟢 안전'
            }.get(account['scenario'], '❓ 알 수 없음')
            
            print(f"{i}. {risk_level}")
            print(f"   📧 이메일: {account['email']}")
            print(f"   📱 전화번호: {account['phone']}")
            print(f"   👤 이름: {account['name']}")
            print()
        
        print("🚀 시연 권장 순서:")
        print("1. victim@breached.org (치명적) → 임팩트 극대화")
        print("2. demo@hackathon.com (높은 위험) → 현실적 사례")
        print("3. secure.person@safe.co.kr (안전) → 대조 효과")
        print("\n💡 scripts/demo_guide.md 파일을 확인하세요!")

if __name__ == "__main__":
    creator = DemoScenarioCreator()
    creator.create_comprehensive_demo_data()