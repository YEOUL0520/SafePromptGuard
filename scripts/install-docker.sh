#!/usr/bin/env bash
set -euo pipefail

echo "[SafePrompt Guard] Docker 설치 확인 (Linux / macOS)"
echo

if command -v docker >/dev/null 2>&1 && docker info >/dev/null 2>&1; then
  echo "Docker가 설치되어 있고 데몬이 동작 중입니다."
  docker version
  echo
  echo "실행: ./scripts/start-judge.sh"
  exit 0
fi

if command -v docker >/dev/null 2>&1; then
  echo "Docker CLI는 있으나 데몬이 꺼져 있습니다. Docker Desktop 또는 sudo systemctl start docker"
  exit 1
fi

echo "Docker가 설치되어 있지 않습니다."
echo
echo "Ubuntu/Debian 예시:"
echo "  https://docs.docker.com/engine/install/ubuntu/"
echo "  sudo apt-get update && sudo apt-get install -y docker.io docker-compose-plugin"
echo "  sudo usermod -aG docker \"\$USER\"   # 재로그인 필요"
echo
echo "macOS:"
echo "  https://docs.docker.com/desktop/setup/install/mac-install/"
echo
echo "설치 후: ./scripts/start-judge.sh"
echo "상세: docs/INSTALL_DOCKER.md"
