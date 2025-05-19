# skala-ai-service-mini-project

AI 윤리 평가 시스템
AI 서비스의 윤리적 평가를 자동화하기 위한 시스템입니다. 이 시스템은 AI 서비스 설명을 입력으로 받아 윤리적 리스크를 평가하고, 개선 방안을 제안하는 최종 보고서를 생성합니다.
주요 기능

서비스 정보 수집 및 분석
AI 윤리 가이드라인 기반 리스크 평가
윤리적 리스크 개선 방안 제안
종합 평가 보고서 생성

설치 방법

저장소 클론

bashgit clone https://github.com/your-username/ai-ethics-evaluation.git
cd ai-ethics-evaluation

가상 환경 생성 및 활성화

bashpython -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

필요 패키지 설치

bashpip install -r requirements.txt

.env 파일 생성 및 API 키 설정

OPENAI_API_KEY=your_openai_api_key
LANGCHAIN_API_KEY=your_langchain_api_key
TAVILY_API_KEY=your_tavily_api_key
사용 방법
bashpython main.py "AI 서비스 설명"
또는 Python 코드에서:
pythonfrom src.workflow.graph import evaluate_ai_service_ethics

service_description = """
ZestAI는 금융 기관을 위한 신용 평가 및 대출 결정 AI 시스템으로, 전통적인 신용 점수 외에도
수천 가지 데이터 포인트를 활용하여 더 정확하고 공정한 대출 심사를 제공합니다.
이 플랫폼은 금융 포용성을 높이고 비전통적인 신용 이력을 가진 사람들에게도
공정한 금융 접근성을 제공하는 것을 목표로 합니다.
"""

result = evaluate_ai_service_ethics(service_description)
print(result["final_report"])
프로젝트 구조

main.py: 메인 실행 파일
src/: 소스 코드

retrieval/: PDF 문서 검색 기능
nodes/: 워크플로우 노드 구현
workflow/: 전체 워크플로우 그래프


data/: 데이터 파일 (AI 윤리 가이드라인 PDF)
config/: 설정 파일

라이센스
MIT