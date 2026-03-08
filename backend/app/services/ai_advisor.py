"""
AI 전략 추천 어드바이저
Claude API를 사용하여 백테스트 결과를 분석하고 전략을 추천한다.
"""
import json
import logging
import os
from typing import Optional

import anthropic

logger = logging.getLogger("mystock.bot")

_client: Optional[anthropic.AsyncAnthropic] = None


def _get_client() -> anthropic.AsyncAnthropic:
    """Anthropic 클라이언트 싱글톤 반환"""
    global _client
    if _client is None:
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY 환경변수가 설정되지 않았습니다.")
        _client = anthropic.AsyncAnthropic(api_key=api_key)
    return _client


_SYSTEM_PROMPT = """당신은 퀀트 투자 전문가이자 주식 분석가입니다.
사용자가 제공하는 백테스트 성과 데이터를 바탕으로 최적 전략을 추천해 주세요.

분석 원칙:
1. 퀀트 관점: 수치 기반 분석 (수익률, MDD, 샤프지수, 승률)
2. 종목 특성 추론: 추세형/박스권/고변동성 여부를 성과로 유추하여 전략 적합성 판단
3. 리스크 관리: MDD와 변동성 기반 경고 제공
4. 포지션 맞춤: 보유 중이면 매도 전략 관점, 관심종목이면 매수 진입 관점

응답은 반드시 아래 JSON 형식으로만 출력하세요 (마크다운 코드블록 없이):
{
  "recommended_strategy": "추천 전략명",
  "confidence": "높음|보통|낮음",
  "analysis": "종목 특성 대비 전략 적합성 분석 (200자 이내)",
  "risk_warning": "리스크 관련 경고 (100자 이내)",
  "position_advice": "보유/관심 여부에 따른 조언 (100자 이내)"
}"""


async def get_ai_recommendation(
    symbol: str,
    stock_name: str,
    results_summary: list[dict],
    is_holding: bool,
    is_watchlist: bool,
) -> dict:
    """
    백테스트 결과를 분석하여 AI 전략 추천을 반환한다.

    Args:
        symbol: 종목코드
        stock_name: 종목명
        results_summary: 전략별 성과 요약 목록
        is_holding: 보유 여부
        is_watchlist: 관심종목 여부

    Returns:
        AI 추천 결과 딕셔너리
    """
    client = _get_client()

    # 포지션 상태 문자열
    position_str = "없음"
    if is_holding and is_watchlist:
        position_str = "보유 중 + 관심종목"
    elif is_holding:
        position_str = "보유 중"
    elif is_watchlist:
        position_str = "관심종목"

    # 전략별 성과 요약 텍스트
    strategies_text = "\n".join([
        f"- {r['strategy_name']}: 수익률 {r['total_return']:.1f}%, "
        f"MDD {r['mdd']:.1f}%, 샤프 {r['sharpe_ratio']:.2f}, "
        f"승률 {r['win_rate']:.1f}%, 거래수 {r['total_trades']}회"
        for r in results_summary
    ])

    user_message = f"""종목: {stock_name} ({symbol})
현재 포지션: {position_str}

전략별 백테스트 성과:
{strategies_text}

위 데이터를 분석하여 최적 전략을 추천해 주세요."""

    try:
        response = await client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=512,
            system=_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_message}],
        )
        text = response.content[0].text.strip()
        return json.loads(text)
    except json.JSONDecodeError as e:
        logger.warning(f"AI 추천 JSON 파싱 실패: {e}, 응답: {text}")
        return _fallback_recommendation(results_summary)
    except anthropic.APIError as e:
        logger.error(f"Anthropic API 오류: {e}")
        raise
    except Exception as e:
        logger.error(f"AI 추천 오류: {e}")
        raise


def _fallback_recommendation(results_summary: list[dict]) -> dict:
    """API 오류 시 가장 높은 샤프지수 전략을 추천하는 폴백"""
    if not results_summary:
        return {
            "recommended_strategy": "N/A",
            "confidence": "낮음",
            "analysis": "분석 가능한 전략이 없습니다.",
            "risk_warning": "충분한 데이터 없음",
            "position_advice": "추가 데이터 수집 후 재시도 권장",
        }
    best = max(results_summary, key=lambda r: r.get("sharpe_ratio", 0))
    return {
        "recommended_strategy": best["strategy_name"],
        "confidence": "낮음",
        "analysis": f"샤프지수 기준 최우수 전략입니다. (샤프 {best.get('sharpe_ratio', 0):.2f})",
        "risk_warning": f"MDD {best.get('mdd', 0):.1f}% — 손실 위험 확인 필요",
        "position_advice": "AI 분석 일시 불가. 수치 기반 추천으로 대체됩니다.",
    }
