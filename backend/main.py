import sys
import time
from contextlib import asynccontextmanager
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from fastapi import FastAPI, File, Query, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from models.schemas import ScanRequest, ScanResponse, ScanLogListResponse
from services.scanner import run_scan
from services import gemma_analyzer
from services import audit_log
from services.notebook_loader import NotebookParseError, prepare_notebook_scan
from constants import ALLOWED_EXTENSIONS, NOTEBOOK_EXTENSIONS, get_file_upload_policy


@asynccontextmanager
async def lifespan(_app: FastAPI):
    audit_log.init_db()
    yield


app = FastAPI(
    title="SafePrompt Guard",
    description="외부 AI 입력 전 유출 위험 검사 · 마스킹 · 안전 프롬프트 생성",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/config")
async def app_config():
    policy = get_file_upload_policy()
    return {
        "allowed_extensions": policy["extensions"],
        "accept_attribute": policy["accept_attribute"],
        "notebook_extensions": list(policy["notebook_extensions"]),
    }


@app.get("/api/health")
async def health():
    gemma_ok = await gemma_analyzer.check_ollama_available()
    policy = get_file_upload_policy()
    return {
        "status": "ok",
        "service": "SafePrompt Guard",
        "gemma_available": gemma_ok,
        "gemma_model": gemma_analyzer.DEFAULT_MODEL,
        "audit_db": str(audit_log.db_path()),
        "allowed_extensions": policy["extensions"],
    }


@app.get("/api/logs", response_model=ScanLogListResponse)
async def list_scan_logs(limit: int = Query(50, ge=1, le=200)):
    return ScanLogListResponse(
        items=audit_log.list_recent(limit),
        db_path=str(audit_log.db_path()),
    )


@app.post("/api/scan", response_model=ScanResponse)
async def scan_text(req: ScanRequest):
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="검사할 텍스트가 비어 있습니다.")

    started = time.perf_counter()
    result = await run_scan(req.text, use_gemma=req.use_gemma)
    duration_ms = int((time.perf_counter() - started) * 1000)

    audit_log.record_scan(
        result=result,
        input_kind="text",
        filename=None,
        duration_ms=duration_ms,
        text_length=len(req.text),
    )
    return result


@app.post("/api/scan/file", response_model=ScanResponse)
async def scan_file(
    file: UploadFile = File(...),
    use_gemma: bool = True,
):
    name = file.filename or "upload.txt"
    ext = Path(name).suffix.lower()
    if ext and ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=(
                "지원하지 않는 파일 형식입니다. 허용: "
                f"{get_file_upload_policy()['extensions_sorted_display']}"
            ),
        )

    raw = await file.read()
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        text = raw.decode("cp949", errors="replace")

    if not text.strip():
        raise HTTPException(status_code=400, detail="파일 내용이 비어 있습니다.")

    notebook_ctx = None
    scan_text = text
    if ext in NOTEBOOK_EXTENSIONS:
        try:
            scan_text, nb, segments = prepare_notebook_scan(text)
            notebook_ctx = (nb, segments)
        except NotebookParseError as e:
            raise HTTPException(status_code=400, detail=str(e)) from e

    started = time.perf_counter()
    result = await run_scan(
        scan_text,
        use_gemma=use_gemma,
        filename=name,
        notebook_ctx=notebook_ctx,
    )
    duration_ms = int((time.perf_counter() - started) * 1000)

    audit_log.record_scan(
        result=result,
        input_kind="file",
        filename=name,
        duration_ms=duration_ms,
        text_length=len(scan_text),
    )
    return result
