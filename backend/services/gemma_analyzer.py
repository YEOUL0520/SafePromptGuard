import json
import re
import httpx
from models.schemas import Finding

OLLAMA_BASE = "http://localhost:11434"
DEFAULT_MODEL = "gemma2:2b"

ANALYSIS_PROMPT = """다음 텍스트에서 외부 AI 서비스에 입력하면 위험할 수 있는 정보를 찾아라.
법적 판단을 하지 말고, 유출 위험 후보만 분류해라.

분류 기준:
- SECRET: API Key, 비밀번호, 토큰, 인증정보
- SOURCE_CODE: 사내 소스코드 또는 핵심 로직
- TRADE_SECRET_CANDIDATE: 내부 알고리즘, 기술 노하우, 제품 설계 정보
- CUSTOMER_INFO: 고객명, 계약정보, 결제정보
- INFRA_INFO: 서버 주소, DB 구조, 내부망 정보
- SAFE: 외부 공유 가능성이 높은 일반 정보

반드시 아래 JSON 형식으로만 답하라. 다른 텍스트는 출력하지 마라.
{{
  "risk_level": "HIGH|MEDIUM|LOW",
  "findings": [
    {{
      "category": "TRADE_SECRET_CANDIDATE",
      "line": 3,
      "reason": "이유",
      "action": "권장 조치"
    }}
  ],
  "summary": "한 줄 요약"
}}

텍스트:
---
{text}
---"""

SAFE_PROMPT_TEMPLATE = """다음 마스킹된 내용을 외부 AI(ChatGPT, Gemini 등)에 질문할 수 있는 안전한 프롬프트로 재작성해라.

조건:
- 마스킹된 값([MASKED_...])은 복원하지 않는다.
- 회사명, 고객명, 내부 서버명, 테이블명을 구체적으로 쓰지 않는다.
- 문제 해결에 필요한 기술적 맥락은 유지한다.
- 한국어로 작성한다.
- 구조: (1) 문제 요약 (2) 현재 상황 bullet (3) 마스킹된 설정/로그 (4) 외부 AI에게 요청할 질문

마스킹된 내용:
---
{masked_text}
---

탐지된 위험 요약:
{summary}
"""


async def check_ollama_available() -> bool:
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            r = await client.get(f"{OLLAMA_BASE}/api/tags")
            return r.status_code == 200
    except Exception:
        return False


async def _ollama_generate(prompt: str, model: str = DEFAULT_MODEL) -> str | None:
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            r = await client.post(
                f"{OLLAMA_BASE}/api/generate",
                json={"model": model, "prompt": prompt, "stream": False},
            )
            if r.status_code != 200:
                return None
            return r.json().get("response", "")
    except Exception:
        return None


def _parse_json_response(raw: str) -> dict | None:
    raw = raw.strip()
    match = re.search(r"\{[\s\S]*\}", raw)
    if not match:
        return None
    try:
        return json.loads(match.group())
    except json.JSONDecodeError:
        return None


async def analyze_with_gemma(text: str) -> tuple[list[Finding], str, str]:
    prompt = ANALYSIS_PROMPT.format(text=text[:8000])
    raw = await _ollama_generate(prompt)
    if not raw:
        return [], "LOW", ""

    data = _parse_json_response(raw)
    if not data:
        return [], "LOW", ""

    findings: list[Finding] = []
    category_labels = {
        "SECRET": "인증/비밀정보",
        "SOURCE_CODE": "사내 소스코드",
        "TRADE_SECRET_CANDIDATE": "영업비밀 후보",
        "CUSTOMER_INFO": "고객/계약 정보",
        "INFRA_INFO": "인프라 정보",
    }

    for item in data.get("findings", []):
        cat = item.get("category", "TRADE_SECRET_CANDIDATE")
        if cat == "SAFE":
            continue
        findings.append(
            Finding(
                type=category_labels.get(cat, "문맥 기반 위험"),
                category=cat,
                value=f"줄 {item.get('line', '?')}",
                line=item.get("line"),
                severity="HIGH" if cat in ("SECRET", "CUSTOMER_INFO") else "MEDIUM",
                reason=item.get("reason", "Gemma 문맥 분석 결과"),
                action=item.get("action"),
                source="gemma",
            )
        )

    return findings, data.get("risk_level", "LOW"), data.get("summary", "")


async def generate_safe_prompt(masked_text: str, summary: str) -> str | None:
    prompt = SAFE_PROMPT_TEMPLATE.format(
        masked_text=masked_text[:6000],
        summary=summary or "민감정보가 마스킹되었습니다.",
    )
    return await _ollama_generate(prompt)


def fallback_safe_prompt(masked_text: str, findings: list[Finding]) -> str:
    types = list({f.type for f in findings[:8]})
    detected = ", ".join(types) if types else "민감정보"

    lines = masked_text.strip().split("\n")
    context_lines = [l for l in lines if l.strip()][:12]
    context_block = "\n".join(context_lines)

    return f"""다음 내용은 외부 AI에 질문하기 전 보안 검사를 거쳤습니다.
{detected} 등 민감한 정보는 마스킹 처리했습니다.

## 문제 상황
아래 마스킹된 로그/설정/문서를 기준으로 원인 분석과 해결 방법을 알려주세요.

## 현재 상황
- 애플리케이션 또는 시스템에서 오류/이슈가 발생한 상태
- 운영 환경과 유사한 조건에서 재현 가능
- 민감한 접속 정보·고객 정보·내부 식별자는 제거됨

## 마스킹된 내용
```
{context_block}
```

## 요청
1. 가능한 원인을 우선순위별로 정리해 주세요.
2. 점검해야 할 설정 항목과 순서를 알려주세요.
3. 재발 방지를 위한 보안·운영 권장사항을 제안해 주세요."""
