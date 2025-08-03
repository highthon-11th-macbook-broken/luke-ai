import hashlib
import time
from typing import List, Dict, Set, Optional
from app.config import settings

class StaticLeakDetector:
    def __init__(self):
        self.email_trie = set()  # 이메일 해시 저장
        self.phone_trie = set()  # 전화번호 해시 저장
        self.name_trie = set()   # 이름 해시 저장
        self.password_patterns = set()  # 비밀번호 패턴 저장
        
    def _hash_value(self, value: str) -> str:
        """값을 SHA256으로 해시화"""
        return hashlib.sha256(value.lower().strip().encode()).hexdigest()
    
    def _normalize_phone(self, phone: str) -> str:
        """전화번호 정규화 (숫자만 추출)"""
        return ''.join(filter(str.isdigit, phone))
    
    def load_leak_database(self, leak_data: Dict[str, List[str]]):
        """유출 데이터베이스 로드"""
        print("정적 유출 DB 로딩 중...")
        start_time = time.time()
        
        # 이메일 처리
        if 'emails' in leak_data:
            for email in leak_data['emails']:
                self.email_trie.add(self._hash_value(email))
        
        # 전화번호 처리
        if 'phones' in leak_data:
            for phone in leak_data['phones']:
                normalized_phone = self._normalize_phone(phone)
                if normalized_phone:
                    self.phone_trie.add(self._hash_value(normalized_phone))
        
        # 이름 처리
        if 'names' in leak_data:
            for name in leak_data['names']:
                self.name_trie.add(self._hash_value(name))
        
        # 비밀번호 패턴 처리
        if 'passwords' in leak_data:
            for password in leak_data['passwords']:
                self.password_patterns.add(password)
        
        load_time = time.time() - start_time
        print(f"정적 유출 DB 로딩 완료: {load_time:.2f}초")
        print(f"이메일: {len(self.email_trie)}개, 전화번호: {len(self.phone_trie)}개, 이름: {len(self.name_trie)}개")
    
    def detect_email(self, email: str) -> Dict:
        """이메일 유출 탐지"""
        start_time = time.time()
        email_hash = self._hash_value(email)
        is_leaked = email_hash in self.email_trie
        
        detection_time = (time.time() - start_time) * 1000  # ms 단위
        
        return {
            'target': email,
            'is_leaked': is_leaked,
            'risk_score': 1.0 if is_leaked else 0.0,
            'detection_time': detection_time,
            'evidence': f"정적 DB에서 발견됨" if is_leaked else None
        }
    
    def detect_phone(self, phone: str) -> Dict:
        """전화번호 유출 탐지"""
        start_time = time.time()
        normalized_phone = self._normalize_phone(phone)
        phone_hash = self._hash_value(normalized_phone)
        is_leaked = phone_hash in self.phone_trie
        
        detection_time = (time.time() - start_time) * 1000  # ms 단위
        
        return {
            'target': phone,
            'is_leaked': is_leaked,
            'risk_score': 1.0 if is_leaked else 0.0,
            'detection_time': detection_time,
            'evidence': f"정적 DB에서 발견됨" if is_leaked else None
        }
    
    def detect_name(self, name: str) -> Dict:
        """이름 유출 탐지"""
        start_time = time.time()
        name_hash = self._hash_value(name)
        is_leaked = name_hash in self.name_trie
        
        detection_time = (time.time() - start_time) * 1000  # ms 단위
        
        return {
            'target': name,
            'is_leaked': is_leaked,
            'risk_score': 1.0 if is_leaked else 0.0,
            'detection_time': detection_time,
            'evidence': f"정적 DB에서 발견됨" if is_leaked else None
        }
    
    def detect_password_pattern(self, password: str) -> Dict:
        """비밀번호 패턴 유사도 탐지 (Levenshtein distance)"""
        start_time = time.time()
        
        # 간단한 패턴 매칭 (실제로는 더 정교한 알고리즘 필요)
        is_similar = any(self._calculate_similarity(password, pattern) > 0.8 
                        for pattern in self.password_patterns)
        
        detection_time = (time.time() - start_time) * 1000  # ms 단위
        
        return {
            'target': password,
            'is_leaked': is_similar,
            'risk_score': 0.8 if is_similar else 0.0,
            'detection_time': detection_time,
            'evidence': f"유사한 패턴 발견" if is_similar else None
        }
    
    def _calculate_similarity(self, str1: str, str2: str) -> float:
        """간단한 문자열 유사도 계산"""
        if not str1 or not str2:
            return 0.0
        
        # 간단한 Jaccard 유사도
        set1 = set(str1.lower())
        set2 = set(str2.lower())
        
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        
        return intersection / union if union > 0 else 0.0
    
    def detect_all(self, email: Optional[str] = None, 
                   phone: Optional[str] = None, 
                   name: Optional[str] = None,
                   password: Optional[str] = None) -> Dict:
        """모든 타입의 정보에 대해 탐지 수행"""
        results = {
            'email': None,
            'phone': None,
            'name': None,
            'password': None,
            'total_time': 0
        }
        
        start_time = time.time()
        
        if email:
            results['email'] = self.detect_email(email)
        
        if phone:
            results['phone'] = self.detect_phone(phone)
        
        if name:
            results['name'] = self.detect_name(name)
        
        if password:
            results['password'] = self.detect_password_pattern(password)
        
        results['total_time'] = (time.time() - start_time) * 1000  # ms 단위
        
        return results 