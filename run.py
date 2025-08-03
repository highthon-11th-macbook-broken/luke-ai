#!/usr/bin/env python3
"""
하이브리드 유출 탐지 시스템 서버 실행 스크립트
"""

import uvicorn
from app.config import settings

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True,
        log_level="info"
    ) 