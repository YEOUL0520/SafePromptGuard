import re
from models.schemas import Finding

RISK_KEYWORDS: list[tuple[str, str, str]] = [
    (r"\b(?:prod|production)\b", "운영 환경 키워드", "INFRA_INFO"),
    (r"\b(?:internal|company|corp)\b", "내부/회사 키워드", "INFRA_INFO"),
    (r"\b(?:customer|client|vip)\b", "고객 관련 키워드", "CUSTOMER_INFO"),
    (r"\b(?:payment|salary|payroll|billing)\b", "결제/급여 키워드", "CUSTOMER_INFO"),
    (r"\b(?:admin|root|superuser)\b", "관리자 계정 키워드", "SECRET"),
    (r"\b(?:credential|secret|private)\b", "인증정보 키워드", "SECRET"),
    (r"\b(?:algorithm|recommendation|ranking)\b", "알고리즘/추천 키워드", "TRADE_SECRET_CANDIDATE"),
    (r"\b(?:contract|단가|계약)\b", "계약/영업 키워드", "TRADE_SECRET_CANDIDATE"),
]

SENSITIVE_FILES = {
    ".env", "application.yml", "application.properties",
    "config.py", "settings.py", "docker-compose.yml",
    "secrets.json", "credentials.json",
}

TABLE_PATTERN = re.compile(
    r"\b(?:tbl_|tb_|customer_|payment_|user_)[\w]+\b|"
    r"(?:고객|결제|주문|계약)[\s]*(?:테이블|table|Table)",
    re.IGNORECASE,
)


def scan_by_rules(text: str, filename: str | None = None) -> list[Finding]:
    findings: list[Finding] = []
    lines = text.split("\n")

    if filename:
        base = filename.lower().split("/")[-1].split("\\")[-1]
        if base in SENSITIVE_FILES or base.endswith((".env", ".pem", ".key")):
            findings.append(
                Finding(
                    type="민감 설정 파일",
                    category="SECRET",
                    value=filename,
                    line=1,
                    severity="HIGH",
                    reason=f"민감 정보가 포함될 수 있는 파일 형식: {base}",
                    action="설정 파일 전체 내용 공유를 피하세요",
                    source="rule",
                )
            )

    for line_no, line in enumerate(lines, 1):
        for pattern, label, category in RISK_KEYWORDS:
            if re.search(pattern, line, re.IGNORECASE):
                findings.append(
                    Finding(
                        type=label,
                        category=category,
                        value=line.strip()[:100],
                        line=line_no,
                        severity="MEDIUM",
                        reason=f"{line_no}번째 줄에서 {label} 발견",
                        action="해당 문맥을 일반화하여 설명하세요",
                        source="rule",
                    )
                )
                break

        for match in TABLE_PATTERN.finditer(line):
            findings.append(
                Finding(
                    type="내부 테이블/엔티티명",
                    category="INFRA_INFO",
                    value=match.group(),
                    line=line_no,
                    severity="MEDIUM",
                    reason="업무 도메인 테이블명이 포함되어 있음",
                    action="테이블명을 [MASKED_TABLE] 등으로 치환하세요",
                    source="rule",
                )
            )

    return findings
