import aiohttp
import asyncio
import re
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
from urllib.parse import urljoin, quote_plus
from app.config import settings

class FreeDetector:
    def __init__(self):
        self.session = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'ko-KR,ko;q=0.9,en;q=0.8',
            },
            timeout=aiohttp.ClientTimeout(total=15)
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def check_breachdirectory(self, query: str) -> Dict:
        """BreachDirectory 무료 검색"""
        try:
            url = "https://breachdirectory.pw/"
            search_url = f"{url}?func=auto&email={quote_plus(query)}"
            
            async with self.session.get(search_url) as response:
                if response.status == 200:
                    content = await response.text()
                    
                    # 결과 확인
                    if "found" in content.lower() or "breach" in content.lower():
                        return {
                            'source': 'breachdirectory',
                            'query': query,
                            'is_leaked': True,
                            'risk_score': 0.8,
                            'evidence': f"BreachDirectory에서 발견됨",
                            'source_url': search_url
                        }
                    else:
                        return {
                            'source': 'breachdirectory',
                            'query': query,
                            'is_leaked': False,
                            'risk_score': 0.0
                        }
                else:
                    return {
                        'source': 'breachdirectory',
                        'query': query,
                        'is_leaked': False,
                        'error': f'HTTP {response.status}',
                        'risk_score': 0.0
                    }
        except Exception as e:
            return {
                'source': 'breachdirectory',
                'query': query,
                'is_leaked': False,
                'error': str(e),
                'risk_score': 0.0
            }
    
    async def check_leakcheck_io(self, query: str) -> Dict:
        """LeakCheck.io 무료 검색"""
        try:
            url = "https://leakcheck.io/"
            search_url = f"{url}?check={quote_plus(query)}&type=auto"
            
            async with self.session.get(search_url) as response:
                if response.status == 200:
                    content = await response.text()
                    
                    # 결과 확인
                    if "found" in content.lower() or "leak" in content.lower():
                        return {
                            'source': 'leakcheck_io',
                            'query': query,
                            'is_leaked': True,
                            'risk_score': 0.7,
                            'evidence': f"LeakCheck.io에서 발견됨",
                            'source_url': search_url
                        }
                    else:
                        return {
                            'source': 'leakcheck_io',
                            'query': query,
                            'is_leaked': False,
                            'risk_score': 0.0
                        }
                else:
                    return {
                        'source': 'leakcheck_io',
                        'query': query,
                        'is_leaked': False,
                        'error': f'HTTP {response.status}',
                        'risk_score': 0.0
                    }
        except Exception as e:
            return {
                'source': 'leakcheck_io',
                'query': query,
                'is_leaked': False,
                'error': str(e),
                'risk_score': 0.0
            }
    
    async def search_github_dorks(self, query: str) -> List[Dict]:
        """GitHub Dork 검색"""
        results = []
        
        # GitHub에서 개인정보 검색
        dorks = [
            f'"{query}"',
            f'"{query}" password',
            f'"{query}" email',
            f'"{query}" leak',
            f'"{query}" breach',
            f'"{query}" dump',
            f'"{query}" database'
        ]
        
        for dork in dorks:
            try:
                search_url = f"https://github.com/search?q={quote_plus(dork)}&type=code"
                
                async with self.session.get(search_url) as response:
                    if response.status == 200:
                        content = await response.text()
                        
                        # 결과가 있는지 확인
                        if "code-list" in content and query.lower() in content.lower():
                            results.append({
                                'source': 'github_dork',
                                'query': query,
                                'dork': dork,
                                'is_leaked': True,
                                'risk_score': 0.6,
                                'evidence': f"GitHub에서 발견됨: {dork}",
                                'source_url': search_url
                            })
                
                await asyncio.sleep(1)  # 요청 간격
                
            except Exception as e:
                print(f"GitHub Dork 검색 실패: {e}")
                continue
        
        return results
    
    async def search_pastebin_dorks(self, query: str) -> List[Dict]:
        """Pastebin Dork 검색"""
        results = []
        
        # Google에서 Pastebin 검색
        dorks = [
            f'site:pastebin.com "{query}"',
            f'site:pastebin.com {query}',
            f'site:paste.ee "{query}"',
            f'site:rentry.co "{query}"'
        ]
        
        for dork in dorks:
            try:
                search_url = f"https://www.google.com/search?q={quote_plus(dork)}"
                
                async with self.session.get(search_url) as response:
                    if response.status == 200:
                        content = await response.text()
                        
                        # 결과가 있는지 확인
                        if "pastebin.com" in content or "paste.ee" in content or "rentry.co" in content:
                            if query.lower() in content.lower():
                                results.append({
                                    'source': 'pastebin_dork',
                                    'query': query,
                                    'dork': dork,
                                    'is_leaked': True,
                                    'risk_score': 0.5,
                                    'evidence': f"Pastebin에서 발견됨: {dork}",
                                    'source_url': search_url
                                })
                
                await asyncio.sleep(2)  # Google 요청 간격
                
            except Exception as e:
                print(f"Pastebin Dork 검색 실패: {e}")
                continue
        
        return results
    
    async def check_all_free_sources(self, email: str = None, phone: str = None, name: str = None) -> List[Dict]:
        """모든 무료 소스 확인"""
        results = []
        
        queries = []
        if email:
            queries.append(email)
        if phone:
            queries.append(phone)
        if name:
            queries.append(name)
        
        for query in queries:
            print(f"🔍 무료 소스 탐지 중: {query}")
            
            # 1. BreachDirectory 확인
            breach_result = await self.check_breachdirectory(query)
            if breach_result.get('is_leaked', False):
                results.append(breach_result)
            
            # 2. LeakCheck.io 확인
            leak_result = await self.check_leakcheck_io(query)
            if leak_result.get('is_leaked', False):
                results.append(leak_result)
            
            # 3. GitHub Dork 검색
            github_results = await self.search_github_dorks(query)
            results.extend(github_results)
            
            # 4. Pastebin Dork 검색
            pastebin_results = await self.search_pastebin_dorks(query)
            results.extend(pastebin_results)
        
        return results 