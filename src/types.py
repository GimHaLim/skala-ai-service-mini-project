from typing import TypedDict, List, Dict, Optional, Any

class GraphState(TypedDict):
    """워크플로우 그래프 상태 정의"""
    service_description: str  # 초기 서비스 설명
    context: Optional[str]  # 검색 결과 컨텍스트
    service_info: Optional[Dict[str, Any]]  # 서비스 분석 결과
    risk_assessment: Optional[Dict[str, Any]]  # 리스크 평가 결과
    improvement_suggestions: Optional[Dict[str, Any]]  # 개선 제안
    final_report: Optional[str]  # 최종 보고서
    messages: List  # 메시지 기록
    next: str  # 다음 단계 지정자