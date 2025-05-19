"""
로깅 설정 모듈
"""

import logging
from langchain_teddynote import logging as ls_logging


def setup_logging():
    """로깅 설정 초기화"""
    # PDF 로깅 설정 - 오류 메시지만 표시
    logging.getLogger('pdfminer').setLevel(logging.ERROR)
    
    # LangSmith 로깅 설정
    ls_logging.langsmith("ai-ethics-evaluation-system")
    
    # 기본 로깅 설정
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    return logging.getLogger(__name__)