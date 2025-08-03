import asyncio
import aiohttp
import time
import re
import json
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, quote_plus
from app.config import settings

class OSINTCrawler:
    def __init__(self):
        self.session = None
        self.crawl_delay = settings.CRAWL_DELAY
        self.max_pages = settings.MAX_CRAWL_PAGES
        self.search_targets = []
        
        # 크롤링 제외 사이트 목록 (로그인/회원가입 페이지 등)
        self.excluded_paths = [
            '/login', '/signin', '/signup', '/register', '/join',
            '/auth', '/account', '/profile', '/settings',
            '/admin', '/moderator', '/dashboard'
        ]
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'ko-KR,ko;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Cache-Control': 'no-cache',
                'Pragma': 'no-cache',
            },
            timeout=aiohttp.ClientTimeout(total=15, connect=10)
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def set_search_targets(self, email: Optional[str] = None, 
                          phone: Optional[str] = None, 
                          name: Optional[str] = None):
        """탐색 대상 설정"""
        self.search_targets = []
        
        if email:
            self.search_targets.append(('email', email))
        if phone:
            self.search_targets.append(('phone', phone))
        if name:
            self.search_targets.append(('name', name))
    
    def _should_skip_url(self, url: str) -> bool:
        """URL이 크롤링에서 제외되어야 하는지 확인"""
        parsed = urlparse(url)
        
        # 제외 경로 확인
        for excluded_path in self.excluded_paths:
            if excluded_path in parsed.path.lower():
                return True
        
        # 파일 확장자 확인 (이미지, PDF 등 제외)
        excluded_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.pdf', '.doc', '.docx', '.xls', '.xlsx']
        for ext in excluded_extensions:
            if parsed.path.lower().endswith(ext):
                return True
        
        return False
    
    async def search_google_dorks(self) -> List[Dict]:
        """Google Dork 검색"""
        results = []
        
        for target_type, target_value in self.search_targets:
            dorks = self._generate_google_dorks(target_type, target_value)
            
            for dork in dorks:
                try:
                    search_url = f"https://www.google.com/search?q={quote_plus(dork)}"
                    async with self.session.get(search_url) as response:
                        if response.status == 200:
                            content = await response.text()
                            found_patterns = self._search_patterns_in_text(content)
                            
                            for pattern_type, value, context in found_patterns:
                                results.append({
                                    'source_url': search_url,
                                    'pattern_type': pattern_type,
                                    'value': value,
                                    'context': context,
                                    'timestamp': time.time(),
                                    'search_method': 'google_dork'
                                })
                    
                    await asyncio.sleep(self.crawl_delay)
                    
                except Exception as e:
                    print(f"Google Dork 검색 실패: {e}")
        
        return results
    
    def _generate_google_dorks(self, target_type: str, target_value: str) -> List[str]:
        """Google Dork 쿼리 생성"""
        dorks = []
        
        if target_type == 'email':
            dorks.extend([
                f'"{target_value}"',
                f'"{target_value}" filetype:txt',
                f'"{target_value}" site:pastebin.com',
                f'"{target_value}" site:github.com',
                f'"{target_value}" intext:"password"',
                f'"{target_value}" intext:"leak"',
            ])
        elif target_type == 'phone':
            dorks.extend([
                f'"{target_value}"',
                f'"{target_value}" filetype:txt',
                f'"{target_value}" site:pastebin.com',
                f'"{target_value}" intext:"개인정보"',
            ])
        elif target_type == 'name':
            dorks.extend([
                f'"{target_value}"',
                f'"{target_value}" filetype:txt',
                f'"{target_value}" intext:"개인정보"',
                f'"{target_value}" intext:"유출"',
            ])
        
        return dorks
    
    async def crawl_forum_sites(self) -> List[Dict]:
        """포럼 사이트 크롤링"""
        forum_sites = [
            'https://www.reddit.com',
            'https://stackoverflow.com',
            'https://github.com',
            'https://paste.ee',
            'https://www.clien.net',
            'https://www.dcinside.com',
            'https://www.inven.co.kr',
            'https://www.ruliweb.com',
            'https://www.ppomppu.co.kr',
            'https://www.fmkorea.com',
            'https://www.82cook.com'
        ]
        
        results = []
        
        for site in forum_sites:
            try:
                print(f"📝 포럼 사이트 크롤링 중: {site}")
                site_results = await self._crawl_site(site)
                results.extend(site_results)
                print(f"✅ {site} 크롤링 완료: {len(site_results)}개 결과")
                await asyncio.sleep(self.crawl_delay)
            except Exception as e:
                print(f"❌ 사이트 크롤링 실패 {site}: {e}")
                continue
        
        return results

    async def crawl_data_leak_sites(self) -> List[Dict]:
        """데이터 유출 사이트 크롤링"""
        leak_sites = [
            'https://haveibeenpwned.com',
            'https://breachdirectory.pw',
            'https://leakcheck.io',
            'https://dehashed.com',
            'https://intelx.io',
            'https://snusbase.com',
            'https://leak-lookup.com',
            'https://weleakinfo.com',
            'https://leakcheck.net',
            'https://leakpeek.com'
        ]
        
        results = []
        
        for site in leak_sites:
            try:
                print(f"🔍 데이터 유출 사이트 크롤링 중: {site}")
                site_results = await self._crawl_site(site)
                results.extend(site_results)
                print(f"✅ {site} 크롤링 완료: {len(site_results)}개 결과")
                await asyncio.sleep(self.crawl_delay)
            except Exception as e:
                print(f"❌ 데이터 유출 사이트 크롤링 실패 {site}: {e}")
                continue
        
        return results

    async def crawl_paste_sites(self) -> List[Dict]:
        """페이스트 사이트 크롤링"""
        paste_sites = [
            'https://pastebin.com',
            'https://paste.ee',
            'https://rentry.co',
            'https://paste.rs',
            'https://paste.gg',
            'https://paste.fo',
            'https://paste.ubuntu.com',
            'https://paste.debian.net',
            'https://paste.kde.org',
            'https://paste.opensuse.org'
        ]
        
        results = []
        
        for site in paste_sites:
            try:
                print(f"📋 페이스트 사이트 크롤링 중: {site}")
                site_results = await self._crawl_site(site)
                results.extend(site_results)
                print(f"✅ {site} 크롤링 완료: {len(site_results)}개 결과")
                await asyncio.sleep(self.crawl_delay)
            except Exception as e:
                print(f"❌ 페이스트 사이트 크롤링 실패 {site}: {e}")
                continue
        
        return results
    
    async def crawl_social_media(self) -> List[Dict]:
        """소셜 미디어 크롤링"""
        social_sites = [
            'https://twitter.com',
            'https://www.facebook.com',
            'https://www.instagram.com',
            'https://www.linkedin.com'
        ]
        
        results = []
        
        for site in social_sites:
            try:
                print(f"📱 소셜 미디어 크롤링 중: {site}")
                site_results = await self._crawl_site(site)
                results.extend(site_results)
                print(f"✅ {site} 크롤링 완료: {len(site_results)}개 결과")
                await asyncio.sleep(self.crawl_delay)
            except Exception as e:
                print(f"❌ 소셜 미디어 크롤링 실패 {site}: {e}")
                continue
        
        return results
    
    async def crawl_dark_web_sources(self) -> List[Dict]:
        """다크웹 소스 크롤링 (시뮬레이션)"""
        # 실제 다크웹 접근은 별도 API 필요
        dark_web_sites = [
            'http://example.onion',  # 시뮬레이션용
            'http://test.onion'      # 시뮬레이션용
        ]
        
        results = []
        
        for site in dark_web_sites:
            try:
                # 실제로는 TOR 네트워크를 통한 접근 필요
                site_results = await self._crawl_site(site)
                results.extend(site_results)
                await asyncio.sleep(self.crawl_delay)
            except Exception as e:
                print(f"다크웹 크롤링 실패 {site}: {e}")
        
        return results
    
    async def _crawl_site(self, base_url: str) -> List[Dict]:
        """특정 사이트 크롤링"""
        results = []
        
        try:
            # 메인 페이지 크롤링
            async with self.session.get(base_url) as response:
                if response.status == 200:
                    content = await response.text()
                    
                    # HTML이 아닌 경우 스킵
                    if not content.strip().startswith('<'):
                        return results
                    
                    soup = BeautifulSoup(content, 'html.parser')
                    
                    # 텍스트에서 개인정보 패턴 검색
                    found_patterns = self._search_patterns_in_text(content)
                    
                    for pattern_type, value, context in found_patterns:
                        results.append({
                            'source_url': base_url,
                            'pattern_type': pattern_type,
                            'value': value,
                            'context': context,
                            'timestamp': time.time(),
                            'search_method': 'direct_crawl'
                        })
                    
                    # 링크 추출 및 추가 페이지 크롤링
                    links = self._extract_links(soup, base_url)
                    
                    # 제외할 링크 필터링
                    filtered_links = [link for link in links if not self._should_skip_url(link)]
                    
                    for link in filtered_links[:self.max_pages]:
                        try:
                            link_results = await self._crawl_page(link)
                            results.extend(link_results)
                            await asyncio.sleep(self.crawl_delay)
                        except Exception as e:
                            print(f"링크 크롤링 실패 {link}: {e}")
                            continue
                            
        except asyncio.TimeoutError:
            print(f"사이트 크롤링 타임아웃: {base_url}")
        except aiohttp.ClientError as e:
            print(f"사이트 크롤링 연결 오류 {base_url}: {e}")
        except Exception as e:
            print(f"사이트 크롤링 오류 {base_url}: {e}")
        
        return results
    
    async def _crawl_page(self, url: str) -> List[Dict]:
        """단일 페이지 크롤링"""
        results = []
        
        # URL 제외 확인
        if self._should_skip_url(url):
            return results
        
        try:
            async with self.session.get(url, timeout=10) as response:
                if response.status == 200:
                    content = await response.text()
                    
                    # HTML이 아닌 경우 스킵
                    if not content.strip().startswith('<'):
                        return results
                    
                    found_patterns = self._search_patterns_in_text(content)
                    
                    for pattern_type, value, context in found_patterns:
                        results.append({
                            'source_url': url,
                            'pattern_type': pattern_type,
                            'value': value,
                            'context': context,
                            'timestamp': time.time(),
                            'search_method': 'page_crawl'
                        })
                        
        except asyncio.TimeoutError:
            print(f"페이지 크롤링 타임아웃: {url}")
        except aiohttp.ClientError as e:
            print(f"페이지 크롤링 연결 오류 {url}: {e}")
        except Exception as e:
            print(f"페이지 크롤링 오류 {url}: {e}")
        
        return results
    
    def _search_patterns_in_text(self, text: str) -> List[tuple]:
        """텍스트에서 개인정보 패턴 검색"""
        found_patterns = []
        
        for target_type, target_value in self.search_targets:
            if target_type == 'email':
                # 이메일 패턴 검색
                email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
                emails = re.findall(email_pattern, text)
                
                for email in emails:
                    if email.lower() == target_value.lower():
                        context = self._extract_context(text, email, 100)
                        found_patterns.append(('email', email, context))
            
            elif target_type == 'phone':
                # 전화번호 패턴 검색 (한국 전화번호 포함)
                phone_patterns = [
                    r'\b\d{3}-\d{3,4}-\d{4}\b',  # 010-1234-5678
                    r'\b\d{10,11}\b',  # 01012345678
                    r'\b\+82-?\d{1,2}-?\d{3,4}-?\d{4}\b',  # +82-10-1234-5678
                    r'\b01[016789]-\d{3,4}-\d{4}\b',  # 한국 휴대폰
                    r'\b0[2-9]{1,2}-\d{3,4}-\d{4}\b',  # 한국 일반전화
                ]
                
                for pattern in phone_patterns:
                    phones = re.findall(pattern, text)
                    for phone in phones:
                        normalized_phone = re.sub(r'[^\d]', '', phone)
                        normalized_target = re.sub(r'[^\d]', '', target_value)
                        
                        if normalized_phone == normalized_target:
                            context = self._extract_context(text, phone, 100)
                            found_patterns.append(('phone', phone, context))
            
            elif target_type == 'name':
                # 이름 패턴 검색 (한국 이름 포함)
                name_patterns = [
                    rf'\b{re.escape(target_value)}\b',  # 정확한 매칭
                    rf'\b{re.escape(target_value)}[씨님]\b',  # 한국 호칭
                    rf'\b{re.escape(target_value)}[가-힣]*\b',  # 한국 이름 확장
                ]
                
                for pattern in name_patterns:
                    names = re.findall(pattern, text, re.IGNORECASE)
                    for name in names:
                        context = self._extract_context(text, name, 100)
                        found_patterns.append(('name', name, context))
        
        return found_patterns
    
    def _extract_context(self, text: str, found_value: str, context_length: int) -> str:
        """발견된 값 주변 컨텍스트 추출"""
        try:
            index = text.find(found_value)
            if index != -1:
                start = max(0, index - context_length)
                end = min(len(text), index + len(found_value) + context_length)
                context = text[start:end].replace('\n', ' ').strip()
                return context
        except:
            pass
        return found_value
    
    def _extract_links(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """페이지에서 링크 추출"""
        links = []
        
        for link in soup.find_all('a', href=True):
            href = link['href']
            full_url = urljoin(base_url, href)
            
            # 같은 도메인의 링크만 수집
            if urlparse(full_url).netloc == urlparse(base_url).netloc:
                links.append(full_url)
        
        return links[:self.max_pages]
    
    async def crawl_all_sources(self) -> List[Dict]:
        """모든 소스에서 크롤링 수행"""
        results = []
        
        if not self.search_targets:
            print("⚠️ 탐색 대상이 설정되지 않았습니다.")
            return results
        
        print(f"🔍 탐색 대상: {[f'{t[0]}:{t[1]}' for t in self.search_targets]}")
        
        # Google Dork 검색
        print("🔍 Google Dork 검색 중...")
        google_results = await self.search_google_dorks()
        results.extend(google_results)
        print(f"✅ Google Dork 검색 완료: {len(google_results)}개 결과")
        
        # 데이터 유출 사이트 크롤링 (우선순위 높음)
        print("🔍 데이터 유출 사이트 크롤링 중...")
        leak_results = await self.crawl_data_leak_sites()
        results.extend(leak_results)
        print(f"✅ 데이터 유출 사이트 크롤링 완료: {len(leak_results)}개 결과")
        
        # 페이스트 사이트 크롤링
        print("📋 페이스트 사이트 크롤링 중...")
        paste_results = await self.crawl_paste_sites()
        results.extend(paste_results)
        print(f"✅ 페이스트 사이트 크롤링 완료: {len(paste_results)}개 결과")
        
        # 포럼 사이트 크롤링
        print("📝 포럼 사이트 크롤링 중...")
        forum_results = await self.crawl_forum_sites()
        results.extend(forum_results)
        print(f"✅ 포럼 사이트 크롤링 완료: {len(forum_results)}개 결과")
        
        # 소셜 미디어 크롤링
        print("📱 소셜 미디어 크롤링 중...")
        social_results = await self.crawl_social_media()
        results.extend(social_results)
        print(f"✅ 소셜 미디어 크롤링 완료: {len(social_results)}개 결과")
        
        # 블로그 사이트 크롤링
        print("📖 블로그 사이트 크롤링 중...")
        blog_results = await self.crawl_blog_sites()
        results.extend(blog_results)
        print(f"✅ 블로그 사이트 크롤링 완료: {len(blog_results)}개 결과")
        
        print(f"🎯 총 크롤링 결과: {len(results)}개")
        return results
    
    async def crawl_blog_sites(self) -> List[Dict]:
        """블로그/뉴스 사이트 크롤링"""
        blog_sites = [
            'https://medium.com',
            'https://dev.to',
            'https://hashnode.dev',
            'https://velog.io',
            'https://tistory.com',
            'https://blog.naver.com',
            'https://brunch.co.kr'
        ]
        
        results = []
        
        for site in blog_sites:
            try:
                site_results = await self._crawl_site(site)
                results.extend(site_results)
                await asyncio.sleep(self.crawl_delay)
            except Exception as e:
                print(f"블로그 사이트 크롤링 실패 {site}: {e}")
        
        return results 