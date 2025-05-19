# AI 윤리 평가 시스템
본 프로젝트는 AI 윤리 평가 에이전트를 설계하고 구현한 실습 프로젝트입니다.

## Overview
- Objective : AI 서비스의 윤리적 리스크를 평가하고 개선 방안을 제시하는 자동화된 시스템 구축
- Methods : RAG(Retrieval-Augmented Generation), Multi-agent Workflow, LLM Chain
- Tools : Web Search, PDF Analysis, Vector Embedding

## Features
- AI 서비스 설명을 입력으로 받아 윤리적 리스크 평가 보고서 자동 생성
- 서비스 정보 검색, 분석, 리스크 평가, 개선안 제안의 완전한 워크플로우 제공
- AI 윤리 가이드라인 기반 데이터 검색 및 활용(RAG)

## Tech Stack 
| Category   | Details                      |
|------------|------------------------------|
| Framework  | LangGraph, LangChain, Python |
| LLM        | GPT-4, GPT-3.5-Turbo via OpenAI API |
| Retrieval  | FAISS, RAG                  |
| Embedding  | OpenAI Text Embedding       |
| Search     | Tavily Search API           |

## Agents
 
- Service Info Agent: 서비스 정보 수집 및 분석
- Risk Assessment Agent: 윤리적 리스크 평가
- Improvement Agent: 개선 방안 제안
- Report Generation Agent: 최종 보고서 생성

## State 
- service_description : AI 서비스에 대한 초기 설명 텍스트
- context : 웹 검색을 통해 수집된 서비스 관련 정보
- service_info : 서비스 분석 결과 (JSON 구조)
- risk_assessment : 윤리적 리스크 평가 결과 (JSON 구조)
- improvement_suggestions : 개선 제안 결과 (JSON 구조)
- final_report : 최종 생성된 마크다운 형식의 보고서
- messages : 워크플로우 진행 중 생성된 메시지 기록
- next : 다음 실행할 노드 이름

## Architecture
![architecture-diagram-perfect](https://github.com/user-attachments/assets/87a8dbf0-3e63-44df-bf83-3bfbf4dee7a4)

## Directory Structure
```
ai_ethics_evaluation/
├── data/                  # AI 윤리 가이드라인 PDF
│   └── Research_on_AI_Ethics_Guidelines.pdf
├── config/                # 설정 파일
│   ├── __init__.py
│   └── logging_config.py  # 로깅 설정
├── src/                   # 소스 코드
│   ├── __init__.py
│   ├── types.py           # 타입 정의
│   ├── retrieval/         # PDF 검색 관련 기능
│   │   ├── __init__.py
│   │   └── pdf_retriever.py
│   ├── nodes/             # 워크플로우 노드
│   │   ├── __init__.py
│   │   ├── service_info.py    # 서비스 정보 검색 노드
│   │   ├── analysis.py        # 서비스 분석 노드
│   │   ├── risk.py            # 윤리적 리스크 평가 노드
│   │   ├── improvement.py     # 개선안 제안 노드
│   │   └── report.py          # 보고서 생성 노드
│   └── workflow/          # 워크플로우 그래프
│       ├── __init__.py
│       └── graph.py       # 워크플로우 그래프 구성
├── main.py                # 메인 실행 스크립트
├── requirements.txt       # 필요한 패키지 목록
└── README.md
```

## Contributors 
- 김하림 : Prompt Engineering, Agent Design, Architecture, RAG Implementation
