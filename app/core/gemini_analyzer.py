import aiohttp
import json
import time
from typing import Dict, List, Optional
from app.config import settings

class GeminiAnalyzer:
    def __init__(self):
        if not settings.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY가 설정되지 않았습니다.")
        
        self.api_key = settings.GEMINI_API_KEY
        self.api_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
        
    async def analyze_leak_context(self, target_info: Dict, crawled_data: List[Dict]) -> List[Dict]:
        """크롤링된 데이터를 Gemini로 분석하여 유출 여부 판단"""
        analyzed_results = []
        
        for data in crawled_data:
            try:
                analysis = await self._analyze_single_context(target_info, data)
                analyzed_results.append(analysis)
            except Exception as e:
                print(f"Gemini 분석 오류: {e}")
                # 오류 시 기본값으로 처리
                analyzed_results.append({
                    'source_url': data.get('source_url', ''),
                    'pattern_type': data.get('pattern_type', ''),
                    'value': data.get('value', ''),
                    'context': data.get('context', ''),
                    'is_leaked': False,
                    'risk_score': 0.0,
                    'ai_reasoning': f"분석 오류: {str(e)}"
                })
        
        return analyzed_results
    
    async def _analyze_single_context(self, target_info: Dict, crawled_data: Dict) -> Dict:
        """단일 크롤링 데이터 분석"""
        
        # 프롬프트 구성
        prompt = self._build_analysis_prompt(target_info, crawled_data)
        
        try:
            # Gemini API 호출
            response = await self._call_gemini_api(prompt)
            analysis_result = self._parse_gemini_response(response)
            
            return {
                'source_url': crawled_data.get('source_url', ''),
                'pattern_type': crawled_data.get('pattern_type', ''),
                'value': crawled_data.get('value', ''),
                'context': crawled_data.get('context', ''),
                'is_leaked': analysis_result.get('is_leaked', False),
                'risk_score': analysis_result.get('risk_score', 0.0),
                'ai_reasoning': analysis_result.get('reasoning', '분석 실패')
            }
            
        except Exception as e:
            print(f"Gemini API 호출 오류: {e}")
            return {
                'source_url': crawled_data.get('source_url', ''),
                'pattern_type': crawled_data.get('pattern_type', ''),
                'value': crawled_data.get('value', ''),
                'context': crawled_data.get('context', ''),
                'is_leaked': False,
                'risk_score': 0.0,
                'ai_reasoning': f"API 오류: {str(e)}"
            }
    
    async def _call_gemini_api(self, prompt: str) -> str:
        """Gemini API 호출"""
        headers = {
            'Content-Type': 'application/json',
            'X-goog-api-key': self.api_key
        }
        
        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": prompt
                        }
                    ]
                }
            ]
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    return result.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', '')
                else:
                    error_text = await response.text()
                    raise Exception(f"Gemini API 오류: {response.status} - {error_text}")
    
    def _build_analysis_prompt(self, target_info: Dict, crawled_data: Dict) -> str:
        """분석을 위한 프롬프트 구성"""
        
        target_str = ", ".join([f"{k}: {v}" for k, v in target_info.items() if v])
        
        prompt = f"""
당신은 개인정보 유출 탐지 전문가입니다. 다음 정보를 분석하여 개인정보 유출 여부를 판단해주세요.

**탐지 대상 정보:**
{target_str}

**발견된 컨텍스트:**
- 패턴 타입: {crawled_data.get('pattern_type', '')}
- 발견된 값: {crawled_data.get('value', '')}
- 컨텍스트: {crawled_data.get('context', '')}
- 소스 URL: {crawled_data.get('source_url', '')}

**분석 기준:**
1. 발견된 값이 실제 개인정보인지 확인
2. 컨텍스트가 유출 상황인지 판단 (예: 해킹, 데이터 유출, 개인정보 노출 등)
3. 위험도를 0.0~1.0 사이로 평가

**응답 형식 (JSON):**
{{
    "is_leaked": true/false,
    "risk_score": 0.0~1.0,
    "reasoning": "판단 근거 설명"
}}

분석 결과를 JSON 형식으로만 응답해주세요.
"""
        
        return prompt
    
    def _parse_gemini_response(self, response_text: str) -> Dict:
        """Gemini 응답을 파싱하여 구조화된 결과 반환"""
        try:
            # JSON 부분 추출
            import re
            
            # JSON 패턴 찾기
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                result = json.loads(json_str)
                
                return {
                    'is_leaked': result.get('is_leaked', False),
                    'risk_score': float(result.get('risk_score', 0.0)),
                    'reasoning': result.get('reasoning', '분석 완료')
                }
            else:
                # JSON이 없으면 텍스트에서 키워드 기반으로 판단
                return self._fallback_analysis(response_text)
                
        except Exception as e:
            print(f"응답 파싱 오류: {e}")
            return self._fallback_analysis(response_text)
    
    def _fallback_analysis(self, response_text: str) -> Dict:
        """JSON 파싱 실패 시 키워드 기반 분석"""
        text_lower = response_text.lower()
        
        # 키워드 기반 위험도 판단
        high_risk_keywords = ['유출', '해킹', '침해', '노출', 'leak', 'hack', 'breach', 'exposed']
        medium_risk_keywords = ['개인정보', 'personal', 'data', '정보']
        
        risk_score = 0.0
        is_leaked = False
        
        for keyword in high_risk_keywords:
            if keyword in text_lower:
                risk_score = 0.8
                is_leaked = True
                break
        
        if not is_leaked:
            for keyword in medium_risk_keywords:
                if keyword in text_lower:
                    risk_score = 0.4
                    break
        
        return {
            'is_leaked': is_leaked,
            'risk_score': risk_score,
            'reasoning': f"키워드 기반 분석: {response_text[:100]}..."
        }
    
    async def analyze_batch(self, target_info: Dict, crawled_data_list: List[Dict]) -> Dict:
        """배치 분석 수행"""
        print(f"Gemini AI 분석 시작: {len(crawled_data_list)}개 데이터")
        
        analyzed_results = []
        high_risk_count = 0
        confirmed_leaks = 0
        
        for data in crawled_data_list:
            analysis = await self._analyze_single_context(target_info, data)
            analyzed_results.append(analysis)
            
            if analysis['is_leaked']:
                confirmed_leaks += 1
            if analysis['risk_score'] >= settings.RISK_THRESHOLD:
                high_risk_count += 1
        
        return {
            'analyzed_results': analyzed_results,
            'total_analyzed': len(analyzed_results),
            'confirmed_leaks': confirmed_leaks,
            'high_risk_count': high_risk_count,
            'average_risk_score': sum(r['risk_score'] for r in analyzed_results) / len(analyzed_results) if analyzed_results else 0.0
        } 