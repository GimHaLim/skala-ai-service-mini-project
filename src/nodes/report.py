"""
보고서 생성 노드
"""

import json
import logging
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage
from langchain_core.prompts import ChatPromptTemplate
from src.types import GraphState

logger = logging.getLogger(__name__)

def generate_report(state: GraphState) -> GraphState:
    """
    AI 서비스에 대한 윤리적 평가 결과를 종합한 보고서를 생성합니다.
    
    Args:
        state (GraphState): 현재 그래프 상태
        
    Returns:
        GraphState: 업데이트된 그래프 상태
    """
    logger.info("최종 보고서 생성 시작")
    service_info = state["service_info"]
    risk_assessment = state["risk_assessment"]
    improvement_suggestions = state["improvement_suggestions"]

    # 가벼운 모델 사용
    llm = ChatOpenAI(model="gpt-3.5-turbo")

    # 간소화된 프롬프트
    report_prompt = """
    # AI 윤리 평가 보고서 생성기

    당신은 AI 서비스의 윤리적 평가 결과를 전문적인 보고서로 작성하는 전문가입니다.

    ## 서비스 정보
    {service_info}

    ## 리스크 평가 결과
    {risk_assessment}

    ## 개선 제안
    {improvement_suggestions}

    ## 보고서 작성 지침
    1. 간결한 언어로 작성하세요.
    2. 보고서 최상단에 "SUMMARY" 단락을 추가하고, 최대 5줄 이내로 전체 평가 결과를 요약하세요.
    3. 서비스 개요, 윤리적 리스크 평가 결과, 개선안을 구분하여 제시하세요.
    4. 경영진을 위한 요약(Executive Summary)을 포함하세요.

    마크다운 형식으로 보고서를 작성하세요. 반드시 "SUMMARY" 단락이 최상단에 위치해야 합니다.
    """

    # JSON 데이터 간소화 - 필요한 필드만 포함
    service_info_slim = {
        "service_name": service_info["service_name"],
        "primary_function": service_info["primary_function"],
        "target_users": service_info["target_users"],
        "decision_impact": service_info.get("decision_impact", ""),
        "risk_flags": service_info["risk_flags"]
    }

    risk_assessment_slim = {
        "highest_risk_area": risk_assessment["highest_risk_area"],
        "overall_risk_score": risk_assessment["overall_risk_score"],
        "summary": risk_assessment["summary"]
    }

    # 필수 평가 항목만 포함
    if "risk_assessments" in risk_assessment:
        high_risk_items = [item for item in risk_assessment["risk_assessments"]
                          if item["category"] == risk_assessment["highest_risk_area"]]
        if len(high_risk_items) > 0:
            risk_assessment_slim["risk_assessments"] = high_risk_items[:1]  # 가장 중요한 1개만 포함

    service_info_str = json.dumps(service_info_slim, ensure_ascii=False)
    risk_assessment_str = json.dumps(risk_assessment_slim, ensure_ascii=False)

    # improvement_suggestions도 간소화
    if "improvement_plan" in improvement_suggestions:
        # 계획에서 최대 2개 항목만 포함
        if len(improvement_suggestions["improvement_plan"]) > 2:
            improvement_suggestions["improvement_plan"] = improvement_suggestions["improvement_plan"][:2]

        # 각 영역의 제안사항도 최대 2개로 제한
        for plan in improvement_suggestions["improvement_plan"]:
            if "suggestions" in plan and len(plan["suggestions"]) > 2:
                plan["suggestions"] = plan["suggestions"][:2]

    improvement_suggestions_str = json.dumps(improvement_suggestions, ensure_ascii=False)

    response = llm.invoke(
        ChatPromptTemplate.from_template(report_prompt).format(
            service_info=service_info_str,
            risk_assessment=risk_assessment_str,
            improvement_suggestions=improvement_suggestions_str
        )
    )

    final_report = response.content
    logger.info("최종 보고서 생성 완료")

    messages = state.get("messages", []).copy()
    messages.append(AIMessage(content="AI 윤리 평가 최종 보고서가 생성되었습니다."))

    return {
        **state,
        "final_report": final_report,
        "messages": messages,
        "next": "end"
    }