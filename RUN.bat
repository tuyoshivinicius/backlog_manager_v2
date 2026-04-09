@echo off

echo ============================================
echo   Backlog Manager
echo ============================================
echo.

:: --------------------------------------------------
:: Verificar se o projeto esta instalado
:: --------------------------------------------------
if not exist ".venv\Scripts\zion-backlog-manager.exe" (
    echo Instalacao nao encontrada. Executando INSTALL.bat...
    echo.
    call INSTALL.bat
    if %errorlevel% neq 0 (
        echo.
        echo Falha na instalacao. Abortando.
        exit /b 1
    )
    echo.
)

:: --------------------------------------------------
:: Executar a aplicacao
:: --------------------------------------------------
echo Iniciando Backlog Manager...
echo.
.venv\Scripts\zion-backlog-manager.exe
