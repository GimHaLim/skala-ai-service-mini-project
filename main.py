#!/usr/bin/env python3
"""
AI 윤리 평가 시스템 - 메인 실행 파일
"""

import argparse
import sys
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# LangSmith 로깅 설정
from config.logging_config import setup_logging
setup_logging()

from src.workflow.graph import evaluate_ai_service_ethics


def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(description="AI 서비스 윤리 평가 시스템")
    parser.add_argument("description", type=str, nargs="?",
                        help="평가할 AI 서비스에 대한 설명")
    args = parser.parse_args()

    # 서비스 설명이 제공되지 않은 경우 예시 사용
    if args.description:
        service_description = args.description
    else:
        service_description = """
        ZestAI는 금융 기관을 위한 신용 평가 및 대출 결정 AI 시스템으로, 전통적인 신용 점수 외에도
        수천 가지 데이터 포인트를 활용하여 더 정확하고 공정한 대출 심사를 제공합니다.
        이 플랫폼은 금융 포용성을 높이고 비전통적인 신용 이력을 가진 사람들에게도
        공정한 금융 접근성을 제공하는 것을 목표로 합니다.
        """
        print("서비스 설명이 제공되지 않아 예시를 사용합니다.")

    # 윤리 평가 실행
    try:
        result = evaluate_ai_service_ethics(service_description)
        
        # 최종 보고서 출력
        print("\n===== AI 윤리 평가 최종 보고서 =====\n")
        print(result["final_report"])
        
        return 0
    except Exception as e:
        print(f"오류 발생: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())