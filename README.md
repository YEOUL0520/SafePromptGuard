# SafePrompt Guard

**외부 AI(ChatGPT, Gemini 등) 입력 전 유출 위험 검사 · 마스킹 · 안전 프롬프트 생성** 웹앱 MVP

## 기능

- **3단계 탐지**: 정규식 → 코드/로그 규칙 → Gemma(Ollama) 문맥 분석
- **자동 마스킹**: API Key, 비밀번호, DB URL, 내부 IP/도메인 등
- **안전 프롬프트 생성**: 외부 AI에 바로 붙여넣을 수 있는 질문문
- **파일 업로드**: `.txt`, `.log`, `.env`, `.py`, `.java` 등

## 실행 방법

### 1. 백엔드 (FastAPI)

```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
uvicorn main:app --reload --port 8001
```

### 2. 프론트엔드 (React + Vite)

```bash
cd frontend
npm install
npm run dev
```

브라우저에서 **http://localhost:5173** 접속

### 3. (선택) Gemma 문맥 분석 — Ollama

```bash
ollama pull gemma2:2b
ollama serve
```

Ollama가 없어도 **정규식 + 규칙 기반** 탐지와 **템플릿 안전 프롬프트**는 동작합니다.

## 데모 시나리오

1. **예시 불러오기** 클릭
2. **유출 위험 검사하기** 클릭
3. 위험도 **높음**, 탐지 항목 확인
4. **안전 프롬프트 복사** → ChatGPT/Gemini에 붙여넣기

## 기술 스택

| 구분 | 기술 |
|------|------|
| Frontend | React, Vite, Lucide Icons |
| Backend | FastAPI, Pydantic |
| 1차 탐지 | 정규식 (AWS Key, JWT, DB URL 등) |
| 2차 탐지 | 개발 문맥 규칙 (prod, internal, .env 등) |
| 3차 탐지 | Gemma via Ollama (로컬) |
| 마스킹 | 위치 기반 + 줄 단위 치환 |

## API

- `GET /api/health` — 서버·Gemma 상태
- `POST /api/scan` — 텍스트 검사 `{ "text": "...", "use_gemma": true }`
- `POST /api/scan/file` — 파일 업로드

## 프로젝트 구조

```
├── backend/
│   ├── main.py
│   ├── models/schemas.py
│   └── services/
│       ├── regex_scanner.py
│       ├── rule_scanner.py
│       ├── gemma_analyzer.py
│       ├── masking.py
│       └── scanner.py
└── frontend/
    └── src/App.jsx
```
