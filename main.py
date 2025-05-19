#!/usr/bin/env python3
"""
AI 윤리 평가 시스템 - 메인 실행 파일
"""

import argparse
import sys
import os
from datetime import datetime
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
    parser.add_argument("--output", "-o", type=str,
                        help="보고서를 저장할 파일 경로 (기본값: 'reports' 폴더)")
    parser.add_argument("--format", "-f", type=str, choices=["md", "txt"], default="md",
                        help="보고서 파일 형식 (md 또는 txt, 기본값: md)")
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
        
        # 보고서 파일로 저장
        save_report_to_file(result["final_report"], args.output, args.format, result["service_info"].get("service_name", "AI_Service") if result["service_info"] else "AI_Service")
        
        return 0
    except Exception as e:
        print(f"오류 발생: {str(e)}")
        return 1


def save_report_to_file(report_content, output_path=None, file_format="md", service_name="AI_Service"):
    """보고서를 파일로 저장합니다.
    
    Args:
        report_content (str): 보고서 내용
        output_path (str): 저장할 파일 경로 (없으면 기본 경로 사용)
        file_format (str): 파일 형식 (md 또는 txt)
        service_name (str): 서비스 이름 (파일명에 사용)
    """
    # 현재 날짜와 시간을 파일명에 포함
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 기본 파일명 생성 (서비스 이름 + 타임스탬프)
    sanitized_service_name = "".join(c if c.isalnum() else "_" for c in service_name)
    default_filename = f"{sanitized_service_name}_{timestamp}.{file_format}"
    
    # 출력 경로가 지정되지 않은 경우 기본 경로 사용
    if output_path is None:
        # reports 디렉토리가 없으면 생성
        reports_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reports")
        os.makedirs(reports_dir, exist_ok=True)
        output_path = os.path.join(reports_dir, default_filename)
    elif os.path.isdir(output_path):
        # 디렉토리가 지정된 경우, 해당 디렉토리에 기본 파일명으로 저장
        output_path = os.path.join(output_path, default_filename)
    
    # 파일 확장자 확인 및 수정
    if not output_path.endswith(f".{file_format}"):
        if ".".join(output_path.split(".")[:-1]):
            # 이미 확장자가 있는 경우 대체
            output_path = ".".join(output_path.split(".")[:-1]) + f".{file_format}"
        else:
            # 확장자가 없는 경우 추가
            output_path += f".{file_format}"
    
    # 파일 저장
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(report_content)
    
    print(f"\n보고서가 저장되었습니다: {output_path}")

if __name__ == "__main__":
    sys.exit(main())