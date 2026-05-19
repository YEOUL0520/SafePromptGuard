import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from services.regex_scanner import scan_by_regex
from services.masking import apply_masking, coalesce_span_findings


JWT = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.abc123"


def test_bearer_jwt_overlap_keeps_tail():
    text = f"Bearer {JWT} keep_this_tail"
    findings = scan_by_regex(text)
    assert any(f.type == "Bearer Token" for f in findings)
    assert any(f.type == "JWT Token" for f in findings)

    coalesced = coalesce_span_findings(findings)
    types = {f.type for f in coalesced}
    assert "JWT Token" not in types
    assert "Bearer Token" in types

    masked = apply_masking(text, findings)
    assert "keep_this_tail" in masked
    assert "[MASKED_TOKEN]" in masked
    assert JWT not in masked


def test_coalesce_same_span_prefers_bearer():
    text = f"Bearer {JWT}"
    findings = scan_by_regex(text)
    coalesced = coalesce_span_findings(findings)
    assert len([f for f in coalesced if f.start is not None]) == 1
    assert coalesced[0].type == "Bearer Token"


if __name__ == "__main__":
    test_bearer_jwt_overlap_keeps_tail()
    test_coalesce_same_span_prefers_bearer()
    print("all masking tests passed")
