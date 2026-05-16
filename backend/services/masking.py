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


def _placeholder(finding: Finding) -> str:
    label = MASK_LABELS.get(finding.type) or CATEGORY_MASK.get(finding.category, "MASKED")
    return f"[{label}]"


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
    masked = mask_by_spans(text, findings)
    return mask_by_lines(masked, findings)
