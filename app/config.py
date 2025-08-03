import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # 데이터베이스 설정
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./leak_detection.db")
    
    # Redis 설정
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # Gemini API 설정
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    
    # 서버 설정
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", "8000"))
    
    # 크롤링 설정
    CRAWL_DELAY = float(os.getenv("CRAWL_DELAY", "2.0"))  # 초 단위 (더 안전하게 증가)
    MAX_CRAWL_PAGES = int(os.getenv("MAX_CRAWL_PAGES", "5"))  # 페이지 수 제한
    CRAWL_TIMEOUT = int(os.getenv("CRAWL_TIMEOUT", "15"))  # 크롤링 타임아웃
    MAX_CONCURRENT_REQUESTS = int(os.getenv("MAX_CONCURRENT_REQUESTS", "3"))  # 동시 요청 수 제한
    
    # 탐지 설정
    DETECTION_TIMEOUT = int(os.getenv("DETECTION_TIMEOUT", "30"))  # 초 단위
    RISK_THRESHOLD = float(os.getenv("RISK_THRESHOLD", "0.8"))  # 위험도 임계값
    
    # API 탐지 설정
    HIBP_API_KEY = os.getenv("HIBP_API_KEY")  # HaveIBeenPwned API 키
    DEHASHED_API_KEY = os.getenv("DEHASHED_API_KEY")  # DeHashed API 키
    INTELX_API_KEY = os.getenv("INTELX_API_KEY")  # Intelligence X API 키

settings = Settings() 