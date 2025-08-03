import asyncio
from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from datetime import datetime

from app.models import DetectionRequest, DetectionResult, UnsolvedCase
from app.core.static_detector import StaticLeakDetector
from app.core.enhanced_osint_crawler import EnhancedOSINTCrawler
from app.core.demo_data_generator import DemoDataGenerator
from app.core.demo_ai_analyzer import DemoAIAnalyzer
from app.core.free_detector import FreeDetector
from app.core.gemini_analyzer import GeminiAnalyzer
from app.config import settings

class DetectionService:
    def __init__(self):
        self.static_detector = StaticLeakDetector()
        self.gemini_analyzer = GeminiAnalyzer()
        self.demo_generator = DemoDataGenerator()
        self.demo_ai_analyzer = DemoAIAnalyzer()
        
        # 유출 데이터베이스 자동 로드 (기존 데이터 사용)
        try:
            from scripts.generate_breach_data import load_breach_data_to_system
            # 기존 데이터가 있으면 사용, 없으면 새로 생성
            leak_data = load_breach_data_to_system(force_regenerate=False)
            self.load_leak_database(leak_data)
            print("✅ 탐지 서비스 초기화 완료 - 유출 데이터베이스 로드됨")
        except Exception as e:
            print(f"⚠️ 유출 데이터베이스 로드 실패: {e}")
        
    def load_leak_database(self, leak_data: Dict):
        """유출 데이터베이스 로드"""
        self.static_detector.load_leak_database(leak_data)
    
    async def perform_api_detection(self, email: Optional[str] = None,
                                   phone: Optional[str] = None,
                                   name: Optional[str] = None) -> List[Dict]:
        """API 기반 탐지 수행"""
        results = []
        
        async with APIDetector() as api_detector:
            try:
                print("🔍 API 기반 탐지 시작...")
                api_results = await api_detector.check_all_apis(email, phone, name)
                
                # API 결과를 탐지 결과 형식으로 변환
                for result in api_results:
                    if result.get('is_leaked', False):
                        converted_result = {
                            'detection_type': f"api_{result['source']}",
                            'target_value': result.get('email') or result.get('query', 'unknown'),
                            'is_leaked': True,
                            'risk_score': result.get('risk_score', 0.8),
                            'evidence': f"{result['source']}에서 발견됨",
                            'source_url': f"https://{result['source']}.com",
                            'detection_time': 0
                        }
                        results.append(converted_result)
                
                print(f"✅ API 탐지 완료: {len(results)}개 결과")
                
            except Exception as e:
                print(f"❌ API 탐지 실패: {e}")
        
        return results
    
    async def perform_free_detection(self, email: Optional[str] = None,
                                    phone: Optional[str] = None,
                                    name: Optional[str] = None) -> List[Dict]:
        """무료 탐지 수행"""
        results = []
        
        async with FreeDetector() as free_detector:
            try:
                print("🔍 무료 탐지 시작...")
                free_results = await free_detector.check_all_free_sources(email, phone, name)
                
                # 무료 탐지 결과를 탐지 결과 형식으로 변환
                for result in free_results:
                    if result.get('is_leaked', False):
                        converted_result = {
                            'detection_type': f"free_{result['source']}",
                            'target_value': result.get('query', 'unknown'),
                            'is_leaked': True,
                            'risk_score': result.get('risk_score', 0.6),
                            'evidence': result.get('evidence', f"{result['source']}에서 발견됨"),
                            'source_url': result.get('source_url'),
                            'detection_time': 0
                        }
                        results.append(converted_result)
                
                print(f"✅ 무료 탐지 완료: {len(results)}개 결과")
                
            except Exception as e:
                print(f"❌ 무료 탐지 실패: {e}")
        
        return results
    
    def perform_detection_sync(self, db: Session, user_id: int, request_id: int,
                              email: Optional[str] = None,
                              phone: Optional[str] = None,
                              name: Optional[str] = None) -> Dict:
        """동기 탐지 수행 (백그라운드 작업용)"""
        
        try:
            print("=== 탐지 시작 ===")
            
            # 1. 정적 DB 탐지
            print("정적 DB 탐지 시작...")
            static_results = self._perform_static_detection_sync(email, phone, name)
            print(f"정적 DB 탐지 완료: {len(static_results)}개 결과")
            
            # 2. 무료 탐지 (API 대신)
            print("무료 탐지 시작...")
            free_results = asyncio.run(self.perform_free_detection(email, phone, name))
            print(f"무료 탐지 완료: {len(free_results)}개 결과")
            
            # 3. OSINT 크롤링 (웹 검색)
            print("OSINT 크롤링 시작...")
            osint_results = asyncio.run(self._perform_osint_crawling(email, phone, name))
            print(f"OSINT 크롤링 완료: {len(osint_results)}개 결과")
            
            # 4. OSINT 결과를 탐지 결과 형식으로 변환
            converted_osint_results = []
            for result in osint_results:
                if 'detection_type' not in result:
                    # OSINT 결과를 탐지 결과 형식으로 변환
                    converted_result = {
                        'detection_type': 'osint_crawl',
                        'target_value': result.get('value', result.get('pattern_type', 'unknown')),
                        'is_leaked': True,  # OSINT에서 발견된 것은 유출로 간주
                        'risk_score': 0.7,  # 중간 위험도
                        'evidence': f"OSINT 크롤링에서 발견: {result.get('context', 'N/A')}",
                        'source_url': result.get('source_url'),
                        'detection_time': result.get('timestamp', 0)
                    }
                    converted_osint_results.append(converted_result)
                else:
                    converted_osint_results.append(result)
            
            # 5. 모든 결과 통합 (무료 + 정적 + OSINT)
            all_results = free_results + static_results + converted_osint_results
            print(f"총 탐지 결과: {len(all_results)}개")
            
            # 6. 결과 저장 (동기 버전 사용)
            print("결과 저장 중...")
            self._save_detection_results_sync(db, request_id, all_results)
            
            # 7. 미제사건 생성 (동기 버전 사용)
            print("미제사건 생성 중...")
            self._create_unsolved_cases_sync(db, user_id, request_id, all_results)
            
            # 8. 요청 상태 업데이트
            detection_request = db.query(DetectionRequest).filter(
                DetectionRequest.id == request_id
            ).first()
            
            if detection_request:
                detection_request.status = "completed"
                detection_request.completed_at = datetime.utcnow()
                db.commit()
                print("요청 상태 업데이트 완료")
            
            print("=== 탐지 완료 ===")
            
            return {
                'status': 'completed',
                'total_results': len(all_results),
                'free_results': len(free_results),
                'static_results': len(static_results),
                'osint_results': len(converted_osint_results),
                'leaked_count': sum(1 for r in all_results if r.get('is_leaked', False)),
                'high_risk_count': sum(1 for r in all_results if r.get('risk_score', 0) >= 0.7)
            }
            
        except Exception as e:
            print(f"❌ 탐지 실패: {e}")
            raise e
    
    async def perform_detection(self, db: Session, user_id: int, 
                               email: Optional[str] = None,
                               phone: Optional[str] = None,
                               name: Optional[str] = None) -> Dict:
        """통합 탐지 수행"""
        
        # 1. 탐지 요청 생성
        detection_request = DetectionRequest(
            user_id=user_id,
            target_email=email,
            target_phone=phone,
            target_name=name,
            status="processing"
        )
        db.add(detection_request)
        db.commit()
        db.refresh(detection_request)
        
        try:
            # 2. 정적 DB 탐지
            static_results = await self._perform_static_detection(email, phone, name)
            
            # 3. OSINT 크롤링
            osint_results = await self._perform_osint_crawling(email, phone, name)
            
            # 4. Gemini AI 분석
            analyzed_results = await self._perform_ai_analysis(
                {'email': email, 'phone': phone, 'name': name}, 
                osint_results
            )
            
            # 5. 결과 저장
            all_results = static_results + analyzed_results
            await self._save_detection_results(db, detection_request.id, all_results)
            
            # 6. 미제사건 생성
            await self._create_unsolved_cases(db, user_id, detection_request.id, all_results)
            
            # 7. 요청 상태 업데이트
            detection_request.status = "completed"
            detection_request.completed_at = datetime.utcnow()
            db.commit()
            
            return {
                'request_id': detection_request.id,
                'status': 'completed',
                'total_results': len(all_results),
                'leaked_count': sum(1 for r in all_results if r.get('is_leaked', False)),
                'high_risk_count': sum(1 for r in all_results if r.get('risk_score', 0) >= settings.RISK_THRESHOLD)
            }
            
        except Exception as e:
            detection_request.status = "failed"
            db.commit()
            raise e
    
    def _perform_static_detection_sync(self, email: Optional[str], 
                                       phone: Optional[str], 
                                       name: Optional[str]) -> List[Dict]:
        """정적 DB 탐지 수행 (동기 버전) - 데모 최적화"""
        print("🔍 정적 DB 탐지 시작...")
        
        # 기존 정적 탐지 수행
        static_results = self.static_detector.detect_all(
            email=email, phone=phone, name=name
        )
        
        results = []
        for result_type, result in static_results.items():
            if result and result_type != 'total_time':
                results.append({
                    'detection_type': 'static_db',
                    'target_value': result['target'],
                    'is_leaked': result['is_leaked'],
                    'risk_score': result['risk_score'],
                    'evidence': result['evidence'],
                    'source_url': None,
                    'detection_time': result['detection_time']
                })
        
        # 데모용 향상된 정적 탐지 결과 추가
        enhanced_results = self.demo_generator.generate_enhanced_static_results(
            email=email, phone=phone, name=name
        )
        results.extend(enhanced_results)
        
        print(f"✅ 정적 DB 탐지 완료: {len(results)}개 결과 (향상된 데모 모드)")
        return results
    
    async def _perform_static_detection(self, email: Optional[str], 
                                       phone: Optional[str], 
                                       name: Optional[str]) -> List[Dict]:
        """정적 DB 탐지 수행"""
        print("정적 DB 탐지 시작...")
        
        static_results = self.static_detector.detect_all(
            email=email, phone=phone, name=name
        )
        
        results = []
        for result_type, result in static_results.items():
            if result and result_type != 'total_time':
                results.append({
                    'detection_type': 'static_db',
                    'target_value': result['target'],
                    'is_leaked': result['is_leaked'],
                    'risk_score': result['risk_score'],
                    'evidence': result['evidence'],
                    'source_url': None,
                    'detection_time': result['detection_time']
                })
        
        print(f"정적 DB 탐지 완료: {len(results)}개 결과")
        return results
    
    async def _perform_osint_crawling(self, email: Optional[str], 
                                     phone: Optional[str], 
                                     name: Optional[str]) -> List[Dict]:
        """Enhanced OSINT 크롤링 수행 (데모 최적화)"""
        print("🔍 Enhanced OSINT 크롤링 시작...")
        
        async with EnhancedOSINTCrawler() as crawler:
            crawler.set_search_targets(email=email, phone=phone, name=name)
            crawled_data = await crawler.crawl_all_sources()
        
        print(f"✅ Enhanced OSINT 크롤링 완료: {len(crawled_data)}개 데이터")
        return crawled_data
    
    async def _perform_ai_analysis(self, target_info: Dict, 
                                   crawled_data: List[Dict]) -> List[Dict]:
        """Enhanced AI 분석 수행 (데모 최적화)"""
        if not crawled_data:
            return []
        
        print("🤖 Enhanced AI 분석 시작...")
        
        # 향상된 AI 분석 수행
        analysis_result = await self.demo_ai_analyzer.analyze_batch_enhanced(
            target_info, crawled_data
        )
        
        # 분석 결과를 탐지 결과 형식으로 변환
        results = []
        for analyzed in analysis_result['analyzed_results']:
            results.append({
                'detection_type': 'osint_crawl_ai',
                'target_value': analyzed['value'],
                'is_leaked': analyzed['is_leaked'],
                'risk_score': analyzed['risk_score'],
                'evidence': analyzed['ai_reasoning'],
                'source_url': analyzed['source_url'],
                'detection_time': 0,  # AI 분석 시간은 별도 측정
                'confidence_level': analyzed.get('confidence_level', 0.8),
                'analysis_method': analyzed.get('analysis_method', 'enhanced_ai')
            })
        
        # AI 인사이트 로깅
        insights = analysis_result.get('ai_insights', {})
        print(f"🧠 AI 분석 완료: {len(results)}개 결과")
        print(f"📊 전체 위험도: {insights.get('overall_risk_level', 'unknown')}")
        print(f"🎯 분석 신뢰도: {insights.get('analysis_confidence', 0)}%")
        
        return results
    
    def _save_detection_results_sync(self, db: Session, request_id: int, 
                               results: List[Dict]):
        """탐지 결과를 데이터베이스에 저장 (동기 버전)"""
        print(f"결과 저장 중: {len(results)}개 결과")
        for result in results:
            print(f"저장할 결과: {result}")
            db_result = DetectionResult(
                request_id=request_id,
                detection_type=result['detection_type'],
                target_value=result['target_value'],
                is_leaked=result['is_leaked'],
                risk_score=result['risk_score'],
                evidence=result['evidence'],
                source_url=result.get('source_url')
            )
            db.add(db_result)
        
        db.commit()
        print(f"결과 저장 완료: {request_id}")
    
    async def _save_detection_results(self, db: Session, request_id: int, 
                                     results: List[Dict]):
        """탐지 결과를 데이터베이스에 저장"""
        for result in results:
            db_result = DetectionResult(
                request_id=request_id,
                detection_type=result['detection_type'],
                target_value=result['target_value'],
                is_leaked=result['is_leaked'],
                risk_score=result['risk_score'],
                evidence=result['evidence'],
                source_url=result.get('source_url')
            )
            db.add(db_result)
        
        db.commit()
    
    def _create_unsolved_cases_sync(self, db: Session, user_id: int, 
                              request_id: int, results: List[Dict]):
        """미제사건 생성 (동기 버전)"""
        for result in results:
            if result['is_leaked'] or result['risk_score'] >= settings.RISK_THRESHOLD:
                case_type = "confirmed_leak" if result['is_leaked'] else "high_risk"
                
                unsolved_case = UnsolvedCase(
                    user_id=user_id,
                    detection_result_id=request_id,  # 실제로는 result_id가 필요
                    case_type=case_type,
                    description=f"{result['detection_type']} 탐지: {result['target_value']}",
                    evidence_data={
                        'target_value': result['target_value'],
                        'risk_score': result['risk_score'],
                        'evidence': result['evidence'],
                        'source_url': result.get('source_url')
                    }
                )
                db.add(unsolved_case)
        
        db.commit()
    
    async def _create_unsolved_cases(self, db: Session, user_id: int, 
                                    request_id: int, results: List[Dict]):
        """미제사건 생성"""
        for result in results:
            if result['is_leaked'] or result['risk_score'] >= settings.RISK_THRESHOLD:
                case_type = "confirmed_leak" if result['is_leaked'] else "high_risk"
                
                unsolved_case = UnsolvedCase(
                    user_id=user_id,
                    detection_result_id=request_id,  # 실제로는 result_id가 필요
                    case_type=case_type,
                    description=f"{result['detection_type']} 탐지: {result['target_value']}",
                    evidence_data={
                        'target_value': result['target_value'],
                        'risk_score': result['risk_score'],
                        'evidence': result['evidence'],
                        'source_url': result.get('source_url')
                    }
                )
                db.add(unsolved_case)
        
        db.commit()
    
    def get_detection_summary(self, db: Session, user_id: int) -> Dict:
        """탐지 요약 정보 조회"""
        from sqlalchemy import func
        
        # 총 요청 수
        total_requests = db.query(DetectionRequest).filter(
            DetectionRequest.user_id == user_id
        ).count()
        
        # 완료된 요청 수
        completed_requests = db.query(DetectionRequest).filter(
            DetectionRequest.user_id == user_id,
            DetectionRequest.status == "completed"
        ).count()
        
        # 유출된 정보 수 (조인 문제 수정)
        leaked_count = db.query(DetectionResult).filter(
            DetectionResult.is_leaked == True
        ).count()
        
        # 고위험 정보 수 (조인 문제 수정)
        high_risk_count = db.query(DetectionResult).filter(
            DetectionResult.risk_score >= settings.RISK_THRESHOLD
        ).count()
        
        # 미제사건 수
        unsolved_cases = db.query(UnsolvedCase).filter(
            UnsolvedCase.user_id == user_id,
            UnsolvedCase.is_resolved == False
        ).count()
        
        return {
            'total_requests': total_requests,
            'completed_requests': completed_requests,
            'leaked_count': leaked_count,
            'high_risk_count': high_risk_count,
            'unsolved_cases': unsolved_cases
        } 