#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
docker compose -f docker-compose.prod.yml --env-file .env.prod down
echo "컨테이너를 종료했습니다."
