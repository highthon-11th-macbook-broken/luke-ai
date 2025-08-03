import aiohttp
import asyncio
from typing import List, Dict, Optional
from app.config import settings

class APIDetector:
    def __init__(self):
        self.session = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'application/json',
            },
            timeout=aiohttp.ClientTimeout(total=30)
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def check_haveibeenpwned(self, email: str) -> Dict:
        """HaveIBeenPwned API로 이메일 유출 확인"""
        try:
            # 실제 API 키가 필요하지만, 여기서는 시뮬레이션
            url = f"https://haveibeenpwned.com/api/v3/breachedaccount/{email}"
            
            # 실제로는 API 키를 헤더에 포함해야 함
            headers = {
                'hibp-api-key': 'your-api-key-here',  # 실제 API 키 필요
                'user-agent': 'LeakDetectionSystem'
            }
            
            async with self.session.get(url, headers=headers) as response:
                if response.status == 200:
                    breaches = await response.json()
                    return {
                        'source': 'haveibeenpwned',
                        'email': email,
                        'is_leaked': True,
                        'breach_count': len(breaches),
                        'breaches': breaches,
                        'risk_score': min(1.0, len(breaches) * 0.2)
                    }
                elif response.status == 404:
                    return {
                        'source': 'haveibeenpwned',
                        'email': email,
                        'is_leaked': False,
                        'breach_count': 0,
                        'breaches': [],
                        'risk_score': 0.0
                    }
                else:
                    return {
                        'source': 'haveibeenpwned',
                        'email': email,
                        'is_leaked': False,
                        'error': f'API 오류: {response.status}',
                        'risk_score': 0.0
                    }
        except Exception as e:
            return {
                'source': 'haveibeenpwned',
                'email': email,
                'is_leaked': False,
                'error': str(e),
                'risk_score': 0.0
            }
    
    async def check_dehashed(self, query: str) -> Dict:
        """DeHashed API로 검색"""
        try:
            # 실제 API 키가 필요
            url = "https://api.dehashed.com/search"
            params = {'query': query}
            headers = {
                'Authorization': 'Token your-api-key-here',  # 실제 API 키 필요
                'Accept': 'application/json'
            }
            
            async with self.session.get(url, params=params, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    entries = data.get('entries', [])
                    return {
                        'source': 'dehashed',
                        'query': query,
                        'is_leaked': len(entries) > 0,
                        'entry_count': len(entries),
                        'entries': entries,
                        'risk_score': min(1.0, len(entries) * 0.3)
                    }
                else:
                    return {
                        'source': 'dehashed',
                        'query': query,
                        'is_leaked': False,
                        'error': f'API 오류: {response.status}',
                        'risk_score': 0.0
                    }
        except Exception as e:
            return {
                'source': 'dehashed',
                'query': query,
                'is_leaked': False,
                'error': str(e),
                'risk_score': 0.0
            }
    
    async def check_intelx(self, query: str) -> Dict:
        """Intelligence X API로 검색"""
        try:
            url = "https://intelx.io/intel"
            params = {
                'term': query,
                'maxresults': 10,
                'media': 0,
                'sort': 4,
                'type': 0
            }
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    results = data.get('results', [])
                    return {
                        'source': 'intelx',
                        'query': query,
                        'is_leaked': len(results) > 0,
                        'result_count': len(results),
                        'results': results,
                        'risk_score': min(1.0, len(results) * 0.2)
                    }
                else:
                    return {
                        'source': 'intelx',
                        'query': query,
                        'is_leaked': False,
                        'error': f'API 오류: {response.status}',
                        'risk_score': 0.0
                    }
        except Exception as e:
            return {
                'source': 'intelx',
                'query': query,
                'is_leaked': False,
                'error': str(e),
                'risk_score': 0.0
            }
    
    async def check_all_apis(self, email: str = None, phone: str = None, name: str = None) -> List[Dict]:
        """모든 API 서비스 확인"""
        results = []
        
        if email:
            print(f"🔍 API 탐지 중: {email}")
            # HaveIBeenPwned 확인
            hibp_result = await self.check_haveibeenpwned(email)
            results.append(hibp_result)
            
            # DeHashed 확인
            dehashed_result = await self.check_dehashed(email)
            results.append(dehashed_result)
            
            # Intelligence X 확인
            intelx_result = await self.check_intelx(email)
            results.append(intelx_result)
        
        if phone:
            print(f"🔍 API 탐지 중: {phone}")
            # DeHashed 확인
            dehashed_result = await self.check_dehashed(phone)
            results.append(dehashed_result)
            
            # Intelligence X 확인
            intelx_result = await self.check_intelx(phone)
            results.append(intelx_result)
        
        if name:
            print(f"🔍 API 탐지 중: {name}")
            # Intelligence X 확인
            intelx_result = await self.check_intelx(name)
            results.append(intelx_result)
        
        return results 