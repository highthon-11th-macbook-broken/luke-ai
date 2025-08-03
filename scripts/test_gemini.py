#!/usr/bin/env python3
"""
Gemini API 테스트 스크립트
"""

import asyncio
import sys
import os
from dotenv import load_dotenv

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.gemini_analyzer import GeminiAnalyzer

async def test_gemini_api():
    """Gemini API 테스트"""
    
    # 환경 변수 로드
    load_dotenv()
    
    try:
        # Gemini 분석기 초기화
        analyzer = GeminiAnalyzer()
        
        # 테스트 데이터
        target_info = {
            'email': 'test@example.com',
            'phone': '010-1234-5678',
            'name': '홍길동'
        }
        
        crawled_data = [
            {
                'source_url': 'https://example.com',
                'pattern_type': 'email',
                'value': 'test@example.com',
                'context': '이메일이 유출되었습니다: test@example.com'
            }
        ]
        
        print("🔍 Gemini API 테스트 시작...")
        
        # 단일 분석 테스트
        result = await analyzer._analyze_single_context(target_info, crawled_data[0])
        
        print("✅ 분석 결과:")
        print(f"   - 유출 여부: {result['is_leaked']}")
        print(f"   - 위험도: {result['risk_score']}")
        print(f"   - 분석 근거: {result['ai_reasoning']}")
        
        # 배치 분석 테스트
        batch_result = await analyzer.analyze_batch(target_info, crawled_data)
        
        print("\n📊 배치 분석 결과:")
        print(f"   - 총 분석 수: {batch_result['total_analyzed']}")
        print(f"   - 확인된 유출: {batch_result['confirmed_leaks']}")
        print(f"   - 고위험 항목: {batch_result['high_risk_count']}")
        print(f"   - 평균 위험도: {batch_result['average_risk_score']:.2f}")
        
        print("\n✅ Gemini API 테스트 완료!")
        
    except Exception as e:
        print(f"❌ Gemini API 테스트 실패: {e}")
        print("\n🔧 확인사항:")
        print("1. .env 파일에 GEMINI_API_KEY가 설정되어 있는지 확인")
        print("2. API 키가 유효한지 확인")
        print("3. 인터넷 연결 상태 확인")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(test_gemini_api()) 