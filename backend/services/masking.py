from models.schemas import Finding

MASK_LABELS: dict[str, str] = {
    "AWS Access Key": "MASKED_AWS_KEY",
    "Private Key": "MASKED_PRIVATE_KEY",
    "JWT Token": "MASKED_JWT",
    "Password": "MASKED_PASSWORD",
    "API Key": "MASKED_API_KEY",
    "Bearer Token": "MASKED_TOKEN",
    "DB URL": "MASKED_DB_URL",
    "Internal IP": "MASKED_INTERNAL_IP",
    "Email": "MASKED_EMAIL",
    "Phone": "MASKED_PHONE",
    "Credit Card": "MASKED_CARD",
    "Internal Domain": "MASKED_DOMAIN",
    "내부 테이블/엔티티명": "MASKED_TABLE",
}

CATEGORY_MASK: dict[str, str] = {
    "SECRET": "MASKED_SECRET",
    "SOURCE_CODE": "MASKED_SOURCE",
    "TRADE_SECRET_CANDIDATE": "MASKED_INTERNAL_LOGIC",
    "CUSTOMER_INFO": "MASKED_CUSTOMER_INFO",
    "INFRA_INFO": "MASKED_INFRA",
}

# 겹치는 span이 있을 때 마스킹·표시에 남길 finding 우선순위 (클수록 우선)
TYPE_MASK_PRIORITY: dict[str, int] = {
    "Bearer Token": 100,
    "Private Key": 95,
    "AWS Access Key": 90,
    "JWT Token": 85,
    "API Key": 80,
    "Password": 75,
    "DB URL": 70,
}


def _placeholder(finding: Finding) -> str:
    label = MASK_LABELS.get(finding.type) or CATEGORY_MASK.get(finding.category, "MASKED")
    return f"[{label}]"


def _span_len(f: Finding) -> int:
    assert f.start is not None and f.end is not None
    return f.end - f.start


def _mask_rank(f: Finding) -> tuple[int, int]:
    return (TYPE_MASK_PRIORITY.get(f.type, 0), _span_len(f))


def _pick_span_winner(a: Finding, b: Finding) -> Finding:
    return a if _mask_rank(a) >= _mask_rank(b) else b


def coalesce_span_findings(findings: list[Finding]) -> list[Finding]:
    """중첩·겹치는 span finding을 하나로 합쳐 마스킹 시 인덱스 깨짐을 방지한다."""
    span_findings = [
        f for f in findings if f.start is not None and f.end is not None and f.end > f.start
    ]
    other = [f for f in findings if f not in span_findings]
    if not span_findings:
        return findings

    # 1) 완전 포함 관계: 바깥 span만 유지 (동일 구간이면 우선순위 높은 타입 유지)
    after_nested: list[Finding] = []
    for f in span_findings:
        drop = False
        for g in span_findings:
            if f is g:
                continue
            if f.start >= g.start and f.end <= g.end:
                if f.start > g.start or f.end < g.end:
                    drop = True
                    break
                if _mask_rank(g) > _mask_rank(f):
                    drop = True
                    break
        if not drop:
            after_nested.append(f)

    # 2) 부분 겹침: 구간 합집합으로 병합
    after_nested.sort(key=lambda f: (f.start, f.end))
    merged: list[Finding] = []
    for f in after_nested:
        if merged and f.start < merged[-1].end:
            last = merged[-1]
            winner = _pick_span_winner(last, f)
            merged[-1] = winner.model_copy(
                update={"start": min(last.start, f.start), "end": max(last.end, f.end)}
            )
        else:
            merged.append(f)

    return other + merged


def mask_by_spans(text: str, findings: list[Finding]) -> str:
    span_findings = [f for f in findings if f.start is not None and f.end is not None]
    span_findings.sort(key=lambda x: x.start, reverse=True)

    result = text
    for f in span_findings:
        ph = _placeholder(f)
        result = result[: f.start] + ph + result[f.end :]
    return result


def mask_by_lines(text: str, findings: list[Finding]) -> str:
    lines = text.split("\n")
    lines_to_mask: dict[int, str] = {}

    for f in findings:
        if f.line is None or f.start is not None:
            continue
        if f.line not in lines_to_mask:
            lines_to_mask[f.line] = _placeholder(f)

    for line_no, placeholder in lines_to_mask.items():
        idx = line_no - 1
        if 0 <= idx < len(lines):
            lines[idx] = placeholder

    return "\n".join(lines)


def apply_masking(text: str, findings: list[Finding]) -> str:
    coalesced = coalesce_span_findings(findings)
    masked = mask_by_spans(text, coalesced)
    return mask_by_lines(masked, coalesced)
