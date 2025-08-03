import random
import hashlib
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from faker import Faker

class DemoDataGenerator:
    """해커톤 데모용 현실적인 유출 데이터 생성기"""
    
    def __init__(self):
        self.fake = Faker(['ko_KR', 'en_US'])
        
        # 실제 유출 사례를 기반으로 한 현실적인 소스 사이트
        self.realistic_sources = [
            "pastebin.com/raw/8X3mN2kL",
            "github.com/leaked-data/collection-1",
            "raidforums.com/Thread-BREACH-2023",
            "darkweb-forum.onion/database-leak",
            "telegram-channel/leaked_accounts",
            "discord-server/data-dump-2024",
            "reddit.com/r/DataBreach/comments/xyz123",
            "twitter.com/hackergroup/status/1234567890",
            "4chan.org/b/thread/912345678",
            "breach-directory.com/search?q=target"
        ]
        
        # 현실적인 유출 시나리오 템플릿
        self.leak_scenarios = [
            {
                "type": "database_breach",
                "context_template": "Database dump from {company} breach - User ID: {user_id}, Email: {email}, Phone: {phone}, Registration: {date}",
                "risk_score_range": (0.8, 1.0),
                "evidence_template": "Found in leaked database dump from {company} data breach"
            },
            {
                "type": "forum_post",
                "context_template": "Username: {username} posting personal info - Contact: {email}, Mobile: {phone}, Location: {location}",
                "risk_score_range": (0.6, 0.8),
                "evidence_template": "Personal information shared in forum discussion"
            },
            {
                "type": "paste_site",
                "context_template": "Account credentials dump: {email}:{password} | Phone: {phone} | Created: {date}",
                "risk_score_range": (0.9, 1.0),
                "evidence_template": "Credentials found in public paste site"
            },
            {
                "type": "social_media",
                "context_template": "Social media profile leak - Name: {name}, Email: {email}, Phone: {phone}, DOB: {dob}",
                "risk_score_range": (0.5, 0.7),
                "evidence_template": "Information scraped from compromised social media profile"
            },
            {
                "type": "shopping_site",
                "context_template": "E-commerce customer data - Order #{order_id}: {name}, {email}, {phone}, Address: {address}",
                "risk_score_range": (0.7, 0.9),
                "evidence_template": "Customer data from e-commerce platform breach"
            }
        ]
        
        # 가짜 회사명 풀
        self.companies = [
            "TechCorp", "DataSoft", "SecureNet", "CloudBase", "InfoSys",
            "DigitalHub", "CyberTech", "NetSolutions", "DataVault", "TechNova"
        ]
    
    def generate_demo_osint_results(self, email: Optional[str] = None,
                                   phone: Optional[str] = None,
                                   name: Optional[str] = None,
                                   target_leak_count: int = 3) -> List[Dict]:
        """데모용 OSINT 크롤링 결과 생성"""
        results = []
        
        # 입력된 정보가 있으면 일부는 실제로 "탐지"되도록 설정
        if email or phone or name:
            # 60% 확률로 입력된 정보가 유출된 것으로 시뮬레이션
            if random.random() < 0.6:
                leaked_scenarios = random.sample(self.leak_scenarios, 
                                               min(target_leak_count, len(self.leak_scenarios)))
                
                for scenario in leaked_scenarios:
                    result = self._create_realistic_leak_result(
                        scenario, email, phone, name
                    )
                    results.append(result)
        
        # 추가로 다른 무작위 유출 데이터도 생성 (배경 노이즈)
        noise_count = random.randint(2, 5)
        for _ in range(noise_count):
            scenario = random.choice(self.leak_scenarios)
            fake_result = self._create_fake_leak_result(scenario)
            results.append(fake_result)
        
        return results
    
    def _create_realistic_leak_result(self, scenario: Dict, 
                                    target_email: Optional[str],
                                    target_phone: Optional[str],
                                    target_name: Optional[str]) -> Dict:
        """실제 입력 정보를 기반으로 한 현실적인 유출 결과 생성"""
        
        # 실제 입력된 정보 사용 (일부는 마스킹)
        email = target_email or self.fake.email()
        phone = target_phone or self.fake.phone_number()
        name = target_name or self.fake.name()
        
        # 시나리오별 컨텍스트 생성
        context = scenario["context_template"].format(
            company=random.choice(self.companies),
            user_id=random.randint(100000, 999999),
            email=self._mask_email(email),
            phone=self._mask_phone(phone),
            name=self._mask_name(name),
            username=self._generate_username(name),
            password="••••••••",
            date=self._random_date(),
            location=self.fake.city(),
            dob=self.fake.date_of_birth(),
            order_id=random.randint(10000, 99999),
            address=self.fake.address()
        )
        
        risk_min, risk_max = scenario["risk_score_range"]
        risk_score = round(random.uniform(risk_min, risk_max), 2)
        
        return {
            'source_url': random.choice(self.realistic_sources),
            'pattern_type': scenario["type"],
            'value': target_email or target_phone or target_name or "unknown",
            'context': context,
            'timestamp': time.time() - random.randint(0, 86400 * 30),  # 최근 30일 내
            'search_method': 'osint_crawl',
            'is_leaked': True,
            'risk_score': risk_score,
            'evidence': scenario["evidence_template"].format(
                company=random.choice(self.companies)
            ),
            'ai_reasoning': self._generate_ai_reasoning(scenario["type"], risk_score)
        }
    
    def _create_fake_leak_result(self, scenario: Dict) -> Dict:
        """완전히 가짜인 배경 노이즈 유출 결과 생성"""
        
        fake_email = self.fake.email()
        fake_phone = self.fake.phone_number()
        fake_name = self.fake.name()
        
        context = scenario["context_template"].format(
            company=random.choice(self.companies),
            user_id=random.randint(100000, 999999),
            email=self._mask_email(fake_email),
            phone=self._mask_phone(fake_phone),
            name=self._mask_name(fake_name),
            username=self._generate_username(fake_name),
            password="••••••••",
            date=self._random_date(),
            location=self.fake.city(),
            dob=self.fake.date_of_birth(),
            order_id=random.randint(10000, 99999),
            address=self.fake.address()
        )
        
        risk_min, risk_max = scenario["risk_score_range"]
        risk_score = round(random.uniform(risk_min, risk_max), 2)
        
        return {
            'source_url': random.choice(self.realistic_sources),
            'pattern_type': scenario["type"],
            'value': fake_email,
            'context': context,
            'timestamp': time.time() - random.randint(0, 86400 * 90),  # 최근 90일 내
            'search_method': 'osint_crawl',
            'is_leaked': True,
            'risk_score': risk_score,
            'evidence': scenario["evidence_template"].format(
                company=random.choice(self.companies)
            ),
            'ai_reasoning': self._generate_ai_reasoning(scenario["type"], risk_score)
        }
    
    def _mask_email(self, email: str) -> str:
        """이메일 마스킹 (현실적인 유출 데이터처럼)"""
        if '@' not in email:
            return email
        
        local, domain = email.split('@', 1)
        if len(local) <= 2:
            return email
        
        masked_local = local[0] + '*' * (len(local) - 2) + local[-1]
        return f"{masked_local}@{domain}"
    
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
    
    def _generate_username(self, name: str) -> str:
        """이름 기반 사용자명 생성"""
        clean_name = ''.join(name.split()).lower()
        return clean_name + str(random.randint(10, 999))
    
    def _random_date(self) -> str:
        """무작위 날짜 생성"""
        start_date = datetime.now() - timedelta(days=365*3)
        end_date = datetime.now()
        random_date = start_date + timedelta(
            seconds=random.randint(0, int((end_date - start_date).total_seconds()))
        )
        return random_date.strftime("%Y-%m-%d")
    
    def _generate_ai_reasoning(self, leak_type: str, risk_score: float) -> str:
        """AI 분석 결과 텍스트 생성"""
        
        reasoning_templates = {
            "database_breach": [
                "데이터베이스 유출 패턴과 일치하는 구조화된 개인정보가 발견되었습니다.",
                "기업 고객 데이터베이스 형태의 정보 노출이 확인되었습니다.",
                "체계적인 데이터 덤프에서 개인정보가 포함된 레코드를 발견했습니다."
            ],
            "forum_post": [
                "온라인 포럼에서 개인정보를 직접 공유한 게시물이 발견되었습니다.",
                "커뮤니티 사이트에서 부주의한 개인정보 노출이 확인되었습니다.",
                "포럼 토론 중 의도치 않은 개인정보 공개가 탐지되었습니다."
            ],
            "paste_site": [
                "페이스트 사이트에 업로드된 계정 정보 덤프에서 발견되었습니다.",
                "공개 텍스트 공유 플랫폼에서 민감한 정보가 노출되었습니다.",
                "해커 그룹이 공유한 계정 정보 리스트에 포함되어 있습니다."
            ],
            "social_media": [
                "소셜미디어 프로필에서 과도한 개인정보 공개가 탐지되었습니다.",
                "SNS 계정 해킹으로 인한 개인정보 유출이 의심됩니다.",
                "소셜 네트워크에서 개인정보가 공개적으로 노출되어 있습니다."
            ],
            "shopping_site": [
                "이커머스 플랫폼 고객 데이터 유출에서 발견되었습니다.",
                "온라인 쇼핑몰 주문 정보 데이터베이스에서 개인정보가 노출되었습니다.",
                "전자상거래 사이트 보안 침해로 인한 고객 정보 유출이 확인되었습니다."
            ]
        }
        
        base_reasoning = random.choice(reasoning_templates.get(leak_type, ["개인정보 유출이 탐지되었습니다."]))
        
        # 위험도에 따른 추가 설명
        if risk_score >= 0.9:
            severity_text = " 매우 높은 위험도로 즉시 대응이 필요합니다."
        elif risk_score >= 0.7:
            severity_text = " 높은 위험도로 신속한 조치가 권장됩니다."
        elif risk_score >= 0.5:
            severity_text = " 중간 위험도로 모니터링이 필요합니다."
        else:
            severity_text = " 낮은 위험도이지만 주의가 필요합니다."
        
        return base_reasoning + severity_text
    
    def generate_enhanced_static_results(self, email: Optional[str] = None,
                                       phone: Optional[str] = None,
                                       name: Optional[str] = None) -> List[Dict]:
        """향상된 정적 DB 탐지 결과 생성 (해커톤 데모용)"""
        results = []
        
        # 입력된 정보 중 일부는 "발견"되도록 설정
        if email and random.random() < 0.7:  # 70% 확률
            results.append({
                'detection_type': 'static_db',
                'target_value': email,
                'is_leaked': True,
                'risk_score': random.uniform(0.8, 1.0),
                'evidence': f"RockYou2021 데이터베이스에서 발견됨 (해시: {hashlib.sha256(email.encode()).hexdigest()[:16]}...)",
                'source_url': None,
                'detection_time': random.uniform(45, 120)
            })
        
        if phone and random.random() < 0.4:  # 40% 확률 (전화번호는 더 희귀)
            results.append({
                'detection_type': 'static_db',
                'target_value': phone,
                'is_leaked': True,
                'risk_score': random.uniform(0.6, 0.9),
                'evidence': f"Collection#3 전화번호 덤프에서 발견됨",
                'source_url': None,
                'detection_time': random.uniform(35, 80)
            })
        
        if name and random.random() < 0.3:  # 30% 확률 (이름은 가장 희귀)
            results.append({
                'detection_type': 'static_db',
                'target_value': name,
                'is_leaked': True,
                'risk_score': random.uniform(0.5, 0.8),
                'evidence': f"BreachCompilation 사용자명 데이터에서 발견됨",
                'source_url': None,
                'detection_time': random.uniform(25, 60)
            })
        
        return results