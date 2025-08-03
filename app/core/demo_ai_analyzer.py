import random
import time
from typing import Dict, List, Optional
from app.core.gemini_analyzer import GeminiAnalyzer

class DemoAIAnalyzer:
    """해커톤 데모 최적화된 AI 분석기"""
    
    def __init__(self):
        try:
            self.gemini_analyzer = GeminiAnalyzer()
            self.use_real_ai = True
        except:
            self.use_real_ai = False
            print("⚠️ Gemini API 비활성화, 데모 모드로 전환")
    
    async def analyze_batch_enhanced(self, target_info: Dict, crawled_data: List[Dict]) -> Dict:
        """향상된 배치 분석 (데모 최적화)"""
        
        if not crawled_data:
            return {
                'analyzed_results': [],
                'summary': {
                    'total_analyzed': 0,
                    'leaked_count': 0,
                    'high_risk_count': 0,
                    'analysis_time': 0
                }
            }
        
        start_time = time.time()
        analyzed_results = []
        
        # 실제 AI 분석과 데모 분석 혼합
        for data in crawled_data:
            try:
                if self.use_real_ai and random.random() < 0.3:  # 30%만 실제 AI 분석
                    # 실제 Gemini AI 분석
                    analysis = await self.gemini_analyzer._analyze_single_context(target_info, data)
                else:
                    # 데모용 AI 분석 시뮬레이션
                    analysis = self._simulate_ai_analysis(target_info, data)
                
                analyzed_results.append(analysis)
                
            except Exception as e:
                print(f"AI 분석 오류: {e}")
                # 오류 시 시뮬레이션 결과 사용
                analysis = self._simulate_ai_analysis(target_info, data)
                analyzed_results.append(analysis)
        
        analysis_time = time.time() - start_time
        
        # 분석 요약 생성
        summary = self._generate_analysis_summary(analyzed_results, analysis_time)
        
        return {
            'analyzed_results': analyzed_results,
            'summary': summary,
            'ai_insights': self._generate_ai_insights(target_info, analyzed_results)
        }
    
    def _simulate_ai_analysis(self, target_info: Dict, crawled_data: Dict) -> Dict:
        """AI 분석 시뮬레이션 (현실적인 결과 생성)"""
        
        # 컨텍스트 기반 위험도 계산
        context = crawled_data.get('context', '').lower()
        pattern_type = crawled_data.get('pattern_type', '')
        
        # 키워드 기반 위험도 평가
        high_risk_keywords = ['password', 'credentials', 'database', 'breach', 'leak', 'hack']
        medium_risk_keywords = ['email', 'phone', 'personal', 'info', 'contact']
        
        risk_score = 0.3  # 기본 위험도
        
        # 컨텍스트 분석
        if any(keyword in context for keyword in high_risk_keywords):
            risk_score += 0.4
        if any(keyword in context for keyword in medium_risk_keywords):
            risk_score += 0.2
        
        # 패턴 타입별 가중치
        pattern_weights = {
            'database_breach': 0.3,
            'paste_site': 0.25,
            'forum_post': 0.15,
            'social_media': 0.1,
            'shopping_site': 0.2
        }
        
        risk_score += pattern_weights.get(pattern_type, 0.1)
        risk_score = min(risk_score, 1.0)  # 최대값 제한
        
        # 유출 여부 판단 (위험도 기반)
        is_leaked = risk_score >= 0.6 or random.random() < risk_score
        
        # AI 추론 텍스트 생성
        reasoning = self._generate_realistic_reasoning(pattern_type, context, risk_score, is_leaked)
        
        return {
            'source_url': crawled_data.get('source_url', ''),
            'pattern_type': pattern_type,
            'value': crawled_data.get('value', ''),
            'context': crawled_data.get('context', ''),
            'is_leaked': is_leaked,
            'risk_score': round(risk_score, 2),
            'ai_reasoning': reasoning,
            'confidence_level': self._calculate_confidence(context, pattern_type),
            'analysis_method': 'hybrid_ai_simulation'
        }
    
    def _generate_realistic_reasoning(self, pattern_type: str, context: str, 
                                    risk_score: float, is_leaked: bool) -> str:
        """현실적인 AI 추론 텍스트 생성"""
        
        base_templates = {
            'database_breach': [
                "구조화된 데이터베이스 형태의 개인정보 노출이 감지되었습니다.",
                "기업 고객 데이터베이스 유출 패턴과 일치하는 정보가 발견되었습니다.",
                "체계적인 데이터 덤프에서 개인정보가 포함된 레코드를 확인했습니다."
            ],
            'paste_site': [
                "페이스트 사이트에 업로드된 민감한 정보가 탐지되었습니다.",
                "공개 텍스트 공유 플랫폼에서 개인정보 노출이 확인되었습니다.",
                "해커 그룹이 공유한 정보 덤프에 개인정보가 포함되어 있습니다."
            ],
            'forum_post': [
                "온라인 포럼에서 부주의한 개인정보 공개가 발견되었습니다.",
                "커뮤니티 토론 중 의도치 않은 개인정보 노출이 탐지되었습니다.",
                "포럼 게시물에서 개인정보가 직접 언급되었습니다."
            ],
            'social_media': [
                "소셜미디어에서 과도한 개인정보 공개가 관찰되었습니다.",
                "SNS 프로필 정보에서 민감한 개인정보가 노출되어 있습니다.",
                "소셜 네트워크 활동을 통해 개인정보가 유추 가능합니다."
            ]
        }
        
        # 기본 추론 선택
        templates = base_templates.get(pattern_type, ["개인정보 관련 내용이 감지되었습니다."])
        base_reasoning = random.choice(templates)
        
        # 컨텍스트 기반 세부 분석
        context_analysis = []
        if 'password' in context.lower():
            context_analysis.append("비밀번호 정보가 함께 노출되어 있어 매우 위험합니다.")
        if 'email' in context.lower():
            context_analysis.append("이메일 주소가 명시적으로 포함되어 있습니다.")
        if 'phone' in context.lower():
            context_analysis.append("전화번호 정보가 함께 노출되었습니다.")
        
        # 위험도별 결론
        if risk_score >= 0.9:
            severity = "즉시 조치가 필요한 매우 높은 위험도입니다."
        elif risk_score >= 0.7:
            severity = "신속한 대응이 권장되는 높은 위험도입니다."
        elif risk_score >= 0.5:
            severity = "주의 깊은 모니터링이 필요한 중간 위험도입니다."
        else:
            severity = "낮은 위험도이지만 지속적인 관찰이 필요합니다."
        
        # 최종 추론 조합
        reasoning_parts = [base_reasoning]
        if context_analysis:
            reasoning_parts.extend(context_analysis)
        reasoning_parts.append(severity)
        
        return " ".join(reasoning_parts)
    
    def _calculate_confidence(self, context: str, pattern_type: str) -> float:
        """분석 신뢰도 계산"""
        confidence = 0.6  # 기본 신뢰도
        
        # 컨텍스트 길이 고려
        if len(context) > 100:
            confidence += 0.1
        if len(context) > 200:
            confidence += 0.1
        
        # 패턴 타입별 신뢰도
        pattern_confidence = {
            'database_breach': 0.2,
            'paste_site': 0.15,
            'forum_post': 0.1,
            'social_media': 0.05,
            'shopping_site': 0.15
        }
        
        confidence += pattern_confidence.get(pattern_type, 0)
        
        # 키워드 존재 여부
        confident_keywords = ['password', 'credentials', 'database', 'email', 'phone']
        if any(keyword in context.lower() for keyword in confident_keywords):
            confidence += 0.1
        
        return min(round(confidence, 2), 1.0)
    
    def _generate_analysis_summary(self, results: List[Dict], analysis_time: float) -> Dict:
        """분석 요약 생성"""
        total_analyzed = len(results)
        leaked_count = sum(1 for r in results if r.get('is_leaked', False))
        high_risk_count = sum(1 for r in results if r.get('risk_score', 0) >= 0.7)
        
        avg_risk_score = 0
        if results:
            avg_risk_score = sum(r.get('risk_score', 0) for r in results) / len(results)
        
        return {
            'total_analyzed': total_analyzed,
            'leaked_count': leaked_count,
            'high_risk_count': high_risk_count,
            'average_risk_score': round(avg_risk_score, 2),
            'analysis_time': round(analysis_time, 2),
            'analysis_efficiency': round(total_analyzed / max(analysis_time, 0.1), 1)
        }
    
    def _generate_ai_insights(self, target_info: Dict, results: List[Dict]) -> Dict:
        """AI 인사이트 생성"""
        
        if not results:
            return {
                'overall_risk_level': 'low',
                'recommendations': ['추가 모니터링을 권장합니다.'],
                'threat_indicators': [],
                'action_items': []
            }
        
        # 전체 위험도 평가
        avg_risk = sum(r.get('risk_score', 0) for r in results) / len(results)
        leaked_results = [r for r in results if r.get('is_leaked', False)]
        
        if avg_risk >= 0.8 or len(leaked_results) >= 3:
            risk_level = 'critical'
        elif avg_risk >= 0.6 or len(leaked_results) >= 2:
            risk_level = 'high'
        elif avg_risk >= 0.4 or len(leaked_results) >= 1:
            risk_level = 'medium'
        else:
            risk_level = 'low'
        
        # 권장사항 생성
        recommendations = self._generate_recommendations(risk_level, leaked_results)
        
        # 위협 지표 분석
        threat_indicators = self._analyze_threat_indicators(results)
        
        # 액션 아이템 생성
        action_items = self._generate_action_items(risk_level, leaked_results)
        
        return {
            'overall_risk_level': risk_level,
            'recommendations': recommendations,
            'threat_indicators': threat_indicators,
            'action_items': action_items,
            'analysis_confidence': round(
                sum(r.get('confidence_level', 0.5) for r in results) / max(len(results), 1), 2
            )
        }
    
    def _generate_recommendations(self, risk_level: str, leaked_results: List[Dict]) -> List[str]:
        """위험도별 권장사항 생성"""
        
        recommendations = []
        
        if risk_level == 'critical':
            recommendations.extend([
                "즉시 해당 계정의 비밀번호를 변경하세요.",
                "2단계 인증을 모든 중요 계정에 설정하세요.",
                "신용카드 및 은행 거래 내역을 확인하세요.",
                "관련 서비스 제공업체에 유출 신고를 하세요."
            ])
        elif risk_level == 'high':
            recommendations.extend([
                "비밀번호 변경을 고려하세요.",
                "계정 보안 설정을 강화하세요.",
                "개인정보 노출 범위를 확인하세요."
            ])
        elif risk_level == 'medium':
            recommendations.extend([
                "정기적인 비밀번호 변경을 권장합니다.",
                "개인정보 공개 설정을 검토하세요."
            ])
        else:
            recommendations.append("현재 위험도는 낮지만 지속적인 모니터링을 권장합니다.")
        
        return recommendations
    
    def _analyze_threat_indicators(self, results: List[Dict]) -> List[str]:
        """위협 지표 분석"""
        indicators = []
        
        # 패턴 분석
        pattern_counts = {}
        for result in results:
            pattern = result.get('pattern_type', 'unknown')
            pattern_counts[pattern] = pattern_counts.get(pattern, 0) + 1
        
        # 고위험 패턴 확인
        if pattern_counts.get('database_breach', 0) > 0:
            indicators.append("데이터베이스 유출 패턴 탐지")
        if pattern_counts.get('paste_site', 0) > 1:
            indicators.append("다중 페이스트 사이트 노출")
        
        # 시간 패턴 분석
        recent_leaks = sum(1 for r in results 
                          if r.get('timestamp', 0) > time.time() - 86400 * 30)  # 최근 30일
        if recent_leaks > 0:
            indicators.append(f"최근 30일 내 {recent_leaks}건 새로운 노출")
        
        return indicators
    
    def _generate_action_items(self, risk_level: str, leaked_results: List[Dict]) -> List[str]:
        """액션 아이템 생성"""
        actions = []
        
        if leaked_results:
            actions.append(f"{len(leaked_results)}개 유출 사례에 대한 상세 조사")
        
        if risk_level in ['critical', 'high']:
            actions.extend([
                "보안팀 즉시 알림",
                "영향받은 계정 목록 작성",
                "사고 대응 절차 시작"
            ])
        
        actions.extend([
            "정기적인 개인정보 노출 스캔 설정",
            "보안 인식 교육 수료"
        ])
        
        return actions