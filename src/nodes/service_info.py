"""
서비스 정보 검색 노드
"""

import logging
from langchain_teddynote.tools.tavily import TavilySearch
from src.types import GraphState

logger = logging.getLogger(__name__)

def search_service_info(state: GraphState) -> GraphState:
    """
    웹 검색을 통해 AI 서비스에 대한 정보를 수집합니다.
    
    Args:
        state (GraphState): 현재 그래프 상태
        
    Returns:
        GraphState: 업데이트된 그래프 상태
    """
    tavily_tool = TavilySearch()
    search_query = state["service_description"] + " AI service features ethics risks"

    logger.info(f"검색 중: {search_query}")

    search_result = tavily_tool.search(
        query=search_query,
        topic="general",
        max_results=5,
        format_output=True,
    )

    # 검색 결과를 상태에 저장
    # 컨텍스트 길이 초과 오류를 방지하기 위해 컨텍스트 크기 제한
    context = "\n".join(search_result)
    
    # 컨텍스트를 적절한 크기(예: 4000자)로 자릅니다.
    max_context_length = 4000
    if len(context) > max_context_length:
        context = context[:max_context_length] + "..." # 잘림을 나타내기 위해 말줄임표 추가

    return {
        **state,
        "context": context,
        "next": "analyze_service"
    }