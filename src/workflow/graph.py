"""
워크플로우 그래프 모듈
"""

import logging
from langchain_core.runnables import RunnableConfig
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_teddynote.messages import random_uuid

from src.types import GraphState
from src.retrieval import setup_pdf_retrieval
from src.nodes import (
    search_service_info,
    analyze_service,
    assess_risks,
    suggest_improvements,
    generate_report
)

logger = logging.getLogger(__name__)

def router(state: GraphState):
    """
    상태에 따라 다음 노드를 결정하는 라우터 함수
    
    Args:
        state (GraphState): 현재 그래프 상태
    
    Returns:
        str: 다음 노드 이름
    """
    return state["next"]

def build_workflow(pdf_retriever, pdf_chain):
    """
    AI 윤리 평가 워크플로우 그래프를 구성합니다.
    
    Args:
        pdf_retriever: PDF 문서 검색기
        pdf_chain: PDF 처리 체인
    
    Returns:
        tuple: (app, initial_state) 워크플로우 앱과 초기 상태
    """
    # 초기 상태 정의
    initial_state = GraphState(
        service_description="",
        context=None,
        service_info=None,
        risk_assessment=None,
        improvement_suggestions=None,
        final_report=None,
        messages=[],
        next="search_service_info"
    )

    # 워크플로우 그래프 생성
    workflow = StateGraph(GraphState)

    # 노드 추가
    workflow.add_node("search_service_info", search_service_info)
    workflow.add_node("analyze_service", analyze_service)
    workflow.add_node("assess_risks", lambda state: assess_risks(state, pdf_retriever, pdf_chain))
    workflow.add_node("suggest_improvements", lambda state: suggest_improvements(state, pdf_retriever))
    workflow.add_node("generate_report", generate_report)

    # 엣지 정의
    workflow.add_conditional_edges(
        "search_service_info",
        router,
        {
            "analyze_service": "analyze_service",
            "end": END
        }
    )

    workflow.add_conditional_edges(
        "analyze_service",
        router,
        {
            "assess_risks": "assess_risks",
            "end": END
        }
    )

    workflow.add_conditional_edges(
        "assess_risks",
        router,
        {
            "suggest_improvements": "suggest_improvements",
            "end": END
        }
    )

    workflow.add_conditional_edges(
        "suggest_improvements",
        router,
        {
            "generate_report": "generate_report",
            "end": END
        }
    )

    workflow.add_conditional_edges(
        "generate_report",
        router,
        {
            "end": END
        }
    )

    # 엔트리 포인트 설정
    workflow.set_entry_point("search_service_info")

    # 메모리 설정 및 컴파일
    memory = MemorySaver()
    app = workflow.compile(checkpointer=memory)

    return app, initial_state

def evaluate_ai_service_ethics(service_description: str):
    """
    AI 서비스의 윤리적 평가를 수행하고 보고서를 생성합니다.
    
    Args:
        service_description (str): AI 서비스에 대한 설명
    
    Returns:
        Dict: 서비스 분석, 리스크 평가, 개선안, 최종 보고서를 포함한 결과
    """
    # PDF 검색 설정
    logger.info("PDF 검색 설정 초기화 중...")
    pdf_retriever, pdf_chain, _ = setup_pdf_retrieval()

    # 워크플로우 구성
    logger.info("워크플로우 구성 중...")
    app, initial_state = build_workflow(pdf_retriever, pdf_chain)

    # 상태 초기화
    config = RunnableConfig(recursion_limit=10, configurable={"thread_id": random_uuid()})

    # 입력값 설정
    state = initial_state.copy()
    state["service_description"] = service_description

    # 워크플로우 실행
    logger.info("AI 서비스 윤리 평가 시작...")
    result = app.invoke(state, config=config)
    logger.info("평가 완료!")

    # 결과 반환
    output = {
        "service_info": result.get("service_info"),
        "risk_assessment": result.get("risk_assessment"),
        "improvement_suggestions": result.get("improvement_suggestions"),
        "final_report": result.get("final_report")
    }

    return output