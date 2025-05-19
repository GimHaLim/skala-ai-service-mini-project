"""
윤리적 리스크 평가 노드
"""

import json
import logging
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_opentutorial.rag.utils import format_docs
from src.types import GraphState

logger = logging.getLogger(__name__)

def assess_risks(state: GraphState, pdf_retriever, pdf_chain) -> GraphState:
    """
    AI 서비스의 윤리적 리스크를 평가합니다.
    
    Args:
        state (GraphState): 현재 그래프 상태
        pdf_retriever: PDF 문서 검색기
        pdf_chain: PDF 처리 체인
        
    Returns:
        GraphState: 업데이트된 그래프 상태
    """
    logger.info("윤리적 리스크 평가 시작")
    service_info = state["service_info"]

    # PDF에서 관련 내용 검색
    query = f"AI 윤리 원칙과 {service_info['primary_function']} 관련 리스크"
    retrieved_docs = pdf_retriever.invoke(query)
    ethics_context = format_docs(retrieved_docs)

    llm = ChatOpenAI(model="gpt-4")

    risk_assessment_prompt = """
    # AI 윤리 리스크 진단 에이전트

    당신은 AI 서비스의 윤리적 리스크를 평가하는 전문가입니다. EU AI Act와 AI 윤리 원칙에 따라
    주어진 AI 서비스의 윤리적 리스크를 진단하세요.

    ## 서비스 정보
    {service_info}

    ## AI 윤리 관련 컨텍스트
    {ethics_context}

    ## 평가 항목
    각 윤리 항목별로 1-5점 척도(1: 매우 낮은 리스크, 5: 매우 높은 리스크)로 평가하고, 상세한 근거를 제시하세요.

    1. **공정성(Fairness)**
       - 서비스가 다양한 인구 집단에 대해 차별 없이 작동하는지 평가

    2. **프라이버시(Privacy)**
       - 개인정보 보호 수준 평가

    3. **투명성(Transparency)**
       - AI 시스템의 작동 방식과 의사결정에 대한 투명성 평가

    4. **안전성(Safety)**
       - 서비스 사용으로 인한 잠재적 위험 평가

    5. **책임성(Accountability)**
       - 문제 발생 시 책임 소재와 해결 방안 평가

    ## 출력 형식
    다음 JSON 구조로 평가 결과를 반환하세요:

    ```json
    {{
      "risk_assessments": [
        {{
          "category": "공정성",
          "score": 3,
          "rationale": "평가 근거 상세 설명",
          "risk_factors": ["위험요소 1", "위험요소 2"],
          "evidence": "발견된 증거"
        }},
        {{
          "category": "프라이버시",
          "score": 4,
          "rationale": "평가 근거 상세 설명",
          "risk_factors": ["위험요소 1", "위험요소 2"],
          "evidence": "발견된 증거"
        }},
        // 나머지 항목도 동일 형식으로 작성
      ],
      "overall_risk_score": 3.6,
      "highest_risk_area": "가장 높은 리스크 영역",
      "summary": "종합적인 리스크 평가 요약"
    }}
    ```
    """

    service_info_str = json.dumps(service_info, ensure_ascii=False)

    response = llm.invoke(
        ChatPromptTemplate.from_template(risk_assessment_prompt).format(
            service_info=service_info_str,
            ethics_context=ethics_context
        )
    )

    try:
        json_str = response.content
        if "```json" in json_str:
            json_str = json_str.split("```json")[1].split("```")[0].strip()
        elif "```" in json_str:
            json_str = json_str.split("```")[1].split("```")[0].strip()

        risk_assessment = json.loads(json_str)
        logger.info(f"리스크 평가 완료: 전체 점수={risk_assessment['overall_risk_score']}")

        messages = state.get("messages", []).copy()

        summary_message = (
            f"윤리적 리스크 평가 완료:\n"
            f"전체 리스크 점수: {risk_assessment['overall_risk_score']}/5\n"
            f"가장 높은 리스크 영역: {risk_assessment['highest_risk_area']}\n"
            f"요약: {risk_assessment['summary']}"
        )

        messages.append(AIMessage(content=summary_message))

        return {
            **state,
            "risk_assessment": risk_assessment,
            "messages": messages,
            "next": "suggest_improvements"
        }
    except Exception as e:
        logger.error(f"리스크 평가 중 오류 발생: {str(e)}")
        messages = state.get("messages", []).copy()
        messages.append(AIMessage(content=f"리스크 평가 중 오류가 발생했습니다: {str(e)}"))
        return {**state, "messages": messages, "next": "end"}