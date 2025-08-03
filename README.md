# 🛡️ 하이브리드 유출 탐지 시스템

정적 유출 DB 탐지와 실시간 OSINT 크롤링을 통합한 개인정보 유출 탐지 시스템입니다.

## 🚀 주요 기능

### 🔍 정적 유출 DB 탐지
- RockYou2021, Collection#1~5, BreachCompilation 등 공개 유출 덤프 사전 인덱싱
- Trie/Set 기반 정적 검색으로 1건당 평균 50~150ms 응답
- SHA256 해시화를 통한 보안 처리

### 🌐 실시간 OSINT 크롤링
- 웹 포럼, 블로그, 커뮤니티, 뉴스 댓글, SNS 등 크롤링
- Scrapy + BeautifulSoup 기반 모듈화된 크롤러
- 사용자 요청 시 즉시 탐색 + 백그라운드 24시간 자동 모니터링

### 🤖 Gemini AI 판단
- Gemini 2.0 Flash API (REST API)를 통한 유출 여부 판단
- 위험도 점수 계산 및 리포트 생성
- 유출로 판단된 항목은 '증거 카드'로 시각화

## 🏗️ 아키텍처

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   FastAPI       │    │   PostgreSQL    │    │     Redis       │
│   (API Server)  │◄──►│   (Database)    │    │   (Cache/Queue) │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Static Detector │    │ Detection       │    │ OSINT Crawler   │
│ (Trie/Set)      │    │ Results         │    │ (Scrapy)        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Gemini Analyzer │    │ Unsolved Cases  │    │ Evidence Cards  │
│ (AI Judgment)   │    │ (High Risk)     │    │ (Visualization) │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 📦 설치 및 실행

### 1. 의존성 설치
```bash
pip install -r requirements.txt
```

### 2. 환경 변수 설정
```bash
cp env.example .env
# .env 파일을 편집하여 실제 값으로 설정
# 특히 GEMINI_API_KEY는 필수!
```

### 3. 데이터베이스 설정
```bash
# PostgreSQL 설치 및 데이터베이스 생성
createdb leak_detection

# Redis 설치 및 실행
redis-server
```

### 4. 유출 데이터 생성
```bash
# Faker를 사용한 현실적인 유출 데이터 생성
python scripts/load_sample_data.py
```

### 5. Celery 워커 실행 (백그라운드 작업용)
```bash
# 터미널 1: Celery 워커 실행
celery -A run_celery.celery_app worker --loglevel=info

# 또는 직접 실행
python run_celery.py
```

### 6. 서버 실행
```bash
# 터미널 2: FastAPI 서버 실행
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 7. 통합 실행 스크립트 (권장)
```bash
# 모든 서비스를 한 번에 실행 (Redis, Celery, FastAPI)
python start_services.py
```

### 8. Docker로 실행
```bash
# 모든 서비스 (FastAPI, Celery, Redis, PostgreSQL) 한 번에 실행
docker-compose up -d

# 로그 확인
docker-compose logs -f

# 서비스 중지
docker-compose down
```

## 📚 API 문서

서버 실행 후 다음 URL에서 API 문서를 확인할 수 있습니다:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🔧 주요 API 엔드포인트

### 탐지 요청
```http
POST /detection/detect
Content-Type: application/json

{
  "email": "user@example.com",
  "phone": "010-1234-5678",
  "name": "홍길동"
}
```

### 탐지 결과 조회
```http
GET /detection/requests/{request_id}
```

### 탐지 요약 정보
```http
GET /detection/summary
```

## 🛠️ 개발 환경

- **Python**: 3.8+
- **FastAPI**: 0.104.1
- **PostgreSQL**: 12+
- **Redis**: 6.0+
- **Celery**: 5.3.4 (백그라운드 작업용)

## 🔒 보안 고려사항

1. **데이터 해시화**: 모든 탐지 대상은 SHA256으로 해시화하여 저장
2. **API 키 관리**: Gemini API 키는 환경 변수로 관리
3. **Rate Limiting**: 크롤링 시 서버 부하 방지를 위한 딜레이 설정
4. **CORS 설정**: 필요한 도메인만 허용

## 📊 성능 지표

- **정적 DB 탐색**: 1건당 150ms 이하
- **OSINT 크롤링**: 평균 5~10초
- **Gemini 응답**: 최대 2초
- **알림 응답성**: 위험도 80% 이상 시 즉시 알림

## 🤝 기여하기

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 🚀 빠른 시작 가이드

1. **환경 변수 설정**
```bash
# .env 파일 편집
nano .env
# GEMINI_API_KEY 필수 설정!
```

2. **의존성 설치**
```bash
pip install -r requirements.txt
```

3. **데이터베이스 설정**
```bash
brew install postgresql redis
brew services start postgresql redis
createdb leak_detection
```

4. **유출 데이터 생성**
```bash
python scripts/load_sample_data.py
```

5. **서버 실행**
```bash
python run.py
```

6. **API 테스트**
```bash
curl -X POST "http://localhost:8000/detection/detect" \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com"}'
```

7. **전체 시스템 테스트**
```bash
python scripts/test_detection.py
```

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 