@echo off
setlocal enabledelayedexpansion

echo ============================================
echo   Backlog Manager - Instalacao Automatizada
echo ============================================
echo.

:: --------------------------------------------------
:: 1. Verificar Python 3.13+
:: --------------------------------------------------
echo [1/3] Verificando Python...

where python >nul 2>&1
if %errorlevel% neq 0 (
    echo ERRO: Python nao encontrado no PATH.
    echo Instale o Python 3.13 ou superior em https://www.python.org/downloads/
    echo Marque "Add Python to PATH" durante a instalacao.
    goto :fail
)

for /f "tokens=2 delims= " %%v in ('python --version 2^>^&1') do set PYTHON_VERSION=%%v
for /f "tokens=1,2 delims=." %%a in ("%PYTHON_VERSION%") do (
    set PYTHON_MAJOR=%%a
    set PYTHON_MINOR=%%b
)

if %PYTHON_MAJOR% lss 3 (
    echo ERRO: Python 3.13+ necessario. Versao encontrada: %PYTHON_VERSION%
    goto :fail
)
if %PYTHON_MAJOR% equ 3 if %PYTHON_MINOR% lss 13 (
    echo ERRO: Python 3.13+ necessario. Versao encontrada: %PYTHON_VERSION%
    goto :fail
)

echo   Python %PYTHON_VERSION% encontrado. OK
echo.

:: --------------------------------------------------
:: 2. Criar ambiente virtual
:: --------------------------------------------------
echo [2/3] Criando ambiente virtual...

if not exist ".venv" (
    python -m venv .venv
    if %errorlevel% neq 0 (
        echo ERRO: Falha ao criar ambiente virtual.
        goto :fail
    )
    echo   Ambiente virtual criado. OK
) else (
    echo   Ambiente virtual ja existe. OK
)
echo.

:: --------------------------------------------------
:: 3. Instalar pacote via pip
:: --------------------------------------------------
echo [3/3] Instalando dependencias do projeto...

if exist "pip.conf" (
    echo   Usando servidor de artefatos customizado (pip.conf)
    set PIP_CONFIG_FILE=pip.conf
)
echo.

.venv\Scripts\pip install .
if %errorlevel% neq 0 (
    echo.
    echo ERRO: Falha ao instalar dependencias.
    goto :fail
)

echo.
echo ============================================
echo   Instalacao concluida com sucesso!
echo ============================================
echo.
echo Para executar o Backlog Manager:
echo   RUN.bat
echo.
goto :eof

:fail
echo.
echo Instalacao abortada.
exit /b 1
