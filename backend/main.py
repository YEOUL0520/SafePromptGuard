import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from models.schemas import ScanRequest, ScanResponse
from services.scanner import run_scan
from services import gemma_analyzer

ALLOWED_EXTENSIONS = {".txt", ".log", ".env", ".py", ".java", ".js", ".ts", ".json", ".yml", ".yaml", ".properties", ".md"}

app = FastAPI(
    title="SafePrompt Guard",
    description="외부 AI 입력 전 유출 위험 검사 · 마스킹 · 안전 프롬프트 생성",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
async def health():
    gemma_ok = await gemma_analyzer.check_ollama_available()
    return {
        "status": "ok",
        "service": "SafePrompt Guard",
        "gemma_available": gemma_ok,
        "gemma_model": gemma_analyzer.DEFAULT_MODEL,
    }


@app.post("/api/scan", response_model=ScanResponse)
async def scan_text(req: ScanRequest):
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="검사할 텍스트가 비어 있습니다.")
    return await run_scan(req.text, use_gemma=req.use_gemma)


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
            detail=f"지원하지 않는 파일 형식입니다. 허용: {', '.join(sorted(ALLOWED_EXTENSIONS))}",
        )

    raw = await file.read()
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        text = raw.decode("cp949", errors="replace")

    if not text.strip():
        raise HTTPException(status_code=400, detail="파일 내용이 비어 있습니다.")

    return await run_scan(text, use_gemma=use_gemma, filename=name)
