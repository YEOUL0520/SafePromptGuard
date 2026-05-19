@echo off
chcp 65001 >nul
echo [SafePrompt Guard] Docker 설치 확인 (Windows)
echo.

docker version >nul 2>&1
if not errorlevel 1 (
    echo Docker가 이미 설치되어 있습니다.
    docker version
    echo.
    echo Docker Desktop이 꺼져 있으면 트레이에서 실행한 뒤 scripts\start-judge.bat 을 사용하세요.
    goto :done
)

echo Docker가 설치되어 있지 않습니다.
echo.
echo 1^) 공식 설치 페이지에서 Docker Desktop 다운로드:
echo    https://docs.docker.com/desktop/setup/install/windows-install/
echo.
echo 2^) winget 으로 설치 ^(관리자 PowerShell^):
echo    winget install -e --id Docker.DockerDesktop
echo.
echo 설치 후 PC를 재부팅하고, Docker Desktop을 실행한 다음
echo   scripts\start-judge.bat
echo 를 실행하세요.
echo.
echo 상세 안내: docs\INSTALL_DOCKER.md
echo.

set /p TRY_WINGET=winget으로 지금 설치를 시도할까요? (Y/N): 
if /i "%TRY_WINGET%"=="Y" (
    winget install -e --id Docker.DockerDesktop
    echo 설치가 끝나면 재부팅 후 Docker Desktop을 실행하세요.
)

:done
pause
