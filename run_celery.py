#!/usr/bin/env python3
"""
Celery 워커 실행 스크립트
이 스크립트를 실행하면 백그라운드에서 탐지 작업이 계속 실행됩니다.
"""

import os
import sys
from celery_app import celery_app

if __name__ == '__main__':
    # Celery 워커 실행
    celery_app.start() 