@echo off
cd /d "%~dp0.."
docker compose -f docker-compose.prod.yml --env-file .env.prod down
echo 컨테이너를 종료했습니다.
