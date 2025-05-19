"""
개선안 제안 노드
"""

import json
import logging
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_teddynote.tools.tavily import TavilySearch
from langchain_opentutorial.rag.utils import format_docs
from src.types import GraphState

logger = logging.getLogger(__name__)

def suggest_improvements(state: GraphState, pdf_retriever) -> GraphState:
    """
    AI 서비스의 윤리적 리스크에 대한 개선안을 제안합니다.
    
    Args:
        state (GraphState): 현재 그래프 상태
        pdf_retriever: PDF 문서 검색기
        
    Returns:
        GraphState: 업데이트된 그래프 상태
    """
    logger.info("개선안 제안 시작")
    service_info = state["service_info"]
    risk_assessment = state["risk_assessment"]

    # 가장 높은 리스크 영역 확인
    highest_risk_area = risk_assessment["highest_risk_area"]
    logger.info(f"최고 리스크 영역: {highest_risk_area}")

    # 관련 사례 검색 (Tavily) - 결과 크기 줄이기
    tavily_tool = TavilySearch()
    search_query = f"AI ethics {highest_risk_area} best practices {service_info['primary_function']}"

    search_result = tavily_tool.search(
        query=search_query,
        topic="general",
        max_results=2,  # 제한된 결과 수
        format_output=True,
    )

    # 검색 결과 텍스트 크기 제한
    max_context_length = 1500  # 더 작은 크기로 제한
    best_practices_context = "\n".join(search_result)
    if len(best_practices_context) > max_context_length:
        best_practices_context = best_practices_context[:max_context_length] + "..."

    # AI 윤리 가이드라인 검색 (RAG)
    query = f"AI 윤리에서 {highest_risk_area} 개선 방법"
    retrieved_docs = pdf_retriever.invoke(query)

    # PDF 컨텍스트 크기 제한
    ethics_guidelines_context = format_docs(retrieved_docs)
    max_pdf_length = 1000  # 더 작은 크기로 제한
    if len(ethics_guidelines_context) > max_pdf_length:
        ethics_guidelines_context = ethics_guidelines_context[:max_pdf_length] + "..."

    # 더 가벼운 모델 사용
    llm = ChatOpenAI(model="gpt-3.5-turbo")

    # 간소화된 프롬프트
    improvement_prompt = """
    # AI 윤리 개선안 제안 에이전트

    당신은 AI 서비스의 윤리적 리스크를 개선하는 전문가입니다. 평가된 리스크를 기반으로 구체적인 개선안을 제안하세요.

    ## 서비스 정보
    {service_info}

    ## 리스크 평가 결과
    {risk_assessment}

    ## 업계 최고 사례
    {best_practices}

    ## AI 윤리 가이드라인
    {ethics_guidelines}

    ## 개선안 제안 지침
    1. 각 리스크 영역별로 구체적이고 실행 가능한 개선안을 제시하세요.
    2. 가장 높은 리스크 영역인 "{highest_risk_area}"에 대해 보다 자세한 개선안을 제공하세요.
    3. 개선안의 기대효과와 구현 난이도를 함께 제시하세요.

    ## 출력 형식
    다음 JSON 구조로 개선안을 반환하세요:
    ```json
    {{
      "priority_area": "{highest_risk_area}",
      "improvement_plan": [
        {{
          "area": "리스크 영역",
          "suggestions": [
            {{
              "title": "개선안 제목",
              "description": "상세 설명",
              "difficulty": "상/중/하",
              "expected_impact": "기대효과"
            }}
          ]
        }}
      ],
      "implementation_roadmap": "전체 개선안 로드맵 요약"
    }}
    ```
    """

    # JSON 데이터 간소화 - 필요한 필드만 포함
    service_info_slim = {
        "service_name": service_info["service_name"],
        "primary_function": service_info["primary_function"],
        "target_users": service_info["target_users"],
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
                          if item["category"] == highest_risk_area or item.get("score", 0) >= 4]
        if high_risk_items:
            risk_assessment_slim["risk_assessments"] = high_risk_items

    service_info_str = json.dumps(service_info_slim, ensure_ascii=False)
    risk_assessment_str = json.dumps(risk_assessment_slim, ensure_ascii=False)

    response = llm.invoke(
        ChatPromptTemplate.from_template(improvement_prompt).format(
            service_info=service_info_str,
            risk_assessment=risk_assessment_str,
            best_practices=best_practices_context,
            ethics_guidelines=ethics_guidelines_context,
            highest_risk_area=highest_risk_area
        )
    )

    try:
        json_str = response.content
        if "```json" in json_str:
            json_str = json_str.split("```json")[1].split("```")[0].strip()
        elif "```" in json_str:
            json_str = json_str.split("```")[1].split("```")[0].strip()

        improvement_suggestions = json.loads(json_str)
        logger.info(f"개선안 작성 완료. 우선 개선 영역: {improvement_suggestions['priority_area']}")

        messages = state.get("messages", []).copy()
        messages.append(AIMessage(content=f"윤리적 리스크 개선안 작성 완료. 최우선 개선 영역: {highest_risk_area}"))

        return {
            **state,
            "improvement_suggestions": improvement_suggestions,
            "messages": messages,
            "next": "generate_report"
        }
    except Exception as e:
        logger.error(f"개선안 작성 중 오류 발생: {str(e)}")
        messages = state.get("messages", []).copy()
        messages.append(AIMessage(content=f"개선안 작성 중 오류가 발생했습니다: {str(e)}"))
        return {**state, "messages": messages, "next": "end"}