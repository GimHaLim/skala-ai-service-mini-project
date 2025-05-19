"""
서비스 분석 노드
"""

import json
import logging
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage
from langchain_core.prompts import ChatPromptTemplate
from src.types import GraphState

logger = logging.getLogger(__name__)

def analyze_service(state: GraphState) -> GraphState:
    """
    AI 서비스의 특성과 기능을 분석합니다.
    
    Args:
        state (GraphState): 현재 그래프 상태
        
    Returns:
        GraphState: 업데이트된 그래프 상태
    """
    logger.info("서비스 분석 시작")
    llm = ChatOpenAI(model="gpt-4")

    prompt = ChatPromptTemplate.from_template("""
    # AI 서비스 분석 에이전트

    당신은 AI 서비스의 특성과 기능을 분석하여 윤리적 리스크 평가의 기초가 될 정보를 제공하는 전문가입니다.

    ## 분석 대상 AI 서비스
    {service_description}

    ## 수집된 정보
    {context}

    ## 분석 지침
    1. 제공된 AI 서비스에 대한 정보를 철저히 분석하세요.
    2. 다음 항목에 관한 정보를 추출하세요:
       - 서비스 이름과 주요 기능
       - 목표 사용자 그룹과 사용 맥락
       - 사용된 데이터 소스 및 모델 유형
       - 의사결정 범위와 영향력 수준
       - 다양한 사용자 그룹에 미치는 영향
       - 개인정보 수집 및 처리 현황

    ## 출력 형식
    다음 JSON 구조로 정보를 반환하세요:

    ```json
    {{
      "service_name": "서비스 이름",
      "primary_function": "주요 기능 간결 설명",
      "detailed_description": "서비스 기능 및 목적 상세 설명",
      "target_users": "주요 사용자 그룹",
      "data_sources": ["데이터 소스 1", "데이터 소스 2"],
      "model_type": "사용된 AI 모델 유형",
      "decision_impact": "의사결정 영향 수준 (높음/중간/낮음)",
      "user_interaction": "사용자 상호작용 방식",
      "risk_flags": {{
        "critical_decisions": true/false,
        "vulnerable_users": true/false,
        "sensitive_topics": true/false,
        "personal_data_processing": true/false,
        "severe_malfunction_risk": true/false
      }},
      "additional_notes": "추가 고려사항"
    }}
    ```

    JSON 형식만 반환하세요.
    """)

    response = llm.invoke(
        prompt.format(
            service_description=state["service_description"],
            context=state["context"]
        )
    )

    try:
        json_str = response.content
        if "```json" in json_str:
            json_str = json_str.split("```json")[1].split("```")[0].strip()
        elif "```" in json_str:
            json_str = json_str.split("```")[1].split("```")[0].strip()

        service_info = json.loads(json_str)
        logger.info(f"서비스 분석 완료: {service_info['service_name']}")

        messages = state.get("messages", []).copy()
        messages.append(AIMessage(content=f"AI 서비스 분석이 완료되었습니다: {service_info['service_name']}"))

        return {
            **state,
            "service_info": service_info,
            "messages": messages,
            "next": "assess_risks"
        }
    except Exception as e:
        logger.error(f"서비스 분석 중 오류 발생: {str(e)}")
        messages = state.get("messages", []).copy()
        messages.append(AIMessage(content=f"서비스 분석 중 오류가 발생했습니다: {str(e)}"))
        return {**state, "messages": messages, "next": "end"}