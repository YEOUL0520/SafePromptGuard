import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from models.schemas import ScanResponse
from services import audit_log


def test_record_and_list():
    with tempfile.TemporaryDirectory() as tmp:
        db_file = Path(tmp) / "test.db"
        import os

        os.environ["SAFE_PROMPT_DB_PATH"] = str(db_file)
        audit_log.init_db()

        result = ScanResponse(
            risk_level="중간",
            risk_score=30,
            findings=[],
            detected_items=[],
            recommendations=[],
            masked_text="ok",
            safe_prompt="ok",
            gemma_available=False,
            gemma_used=False,
            source_kind="text",
        )
        row_id = audit_log.record_scan(
            result=result,
            input_kind="text",
            filename=None,
            duration_ms=42,
            text_length=100,
        )
        assert row_id >= 1

        items = audit_log.list_recent(10)
        assert len(items) == 1
        assert items[0].risk_level == "중간"
        assert items[0].duration_ms == 42
        assert items[0].findings_count == 0

        del os.environ["SAFE_PROMPT_DB_PATH"]


if __name__ == "__main__":
    test_record_and_list()
    print("audit_log tests passed")
