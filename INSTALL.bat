@echo off
setlocal enabledelayedexpansion

echo ============================================
echo   Backlog Manager - Instalacao Automatizada
echo ============================================
echo.

:: --------------------------------------------------
:: 1. Verificar Python 3.11+
:: --------------------------------------------------
echo [1/3] Verificando Python...

where python >nul 2>&1
if %errorlevel% neq 0 (
    echo ERRO: Python nao encontrado no PATH.
    echo Instale o Python 3.11 ou superior em https://www.python.org/downloads/
    echo Marque "Add Python to PATH" durante a instalacao.
    goto :fail
)

for /f "tokens=2 delims= " %%v in ('python --version 2^>^&1') do set PYTHON_VERSION=%%v
for /f "tokens=1,2 delims=." %%a in ("%PYTHON_VERSION%") do (
    set PYTHON_MAJOR=%%a
    set PYTHON_MINOR=%%b
)

if %PYTHON_MAJOR% lss 3 (
    echo ERRO: Python 3.11+ necessario. Versao encontrada: %PYTHON_VERSION%
    goto :fail
)
if %PYTHON_MAJOR% equ 3 if %PYTHON_MINOR% lss 11 (
    echo ERRO: Python 3.11+ necessario. Versao encontrada: %PYTHON_VERSION%
    goto :fail
)

echo   Python %PYTHON_VERSION% encontrado. OK
echo.

:: --------------------------------------------------
:: 2. Verificar/Instalar Poetry
:: --------------------------------------------------
echo [2/3] Verificando Poetry...

where poetry >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=3 delims= " %%v in ('poetry --version 2^>^&1') do set POETRY_VERSION=%%v
    echo   Poetry !POETRY_VERSION! encontrado. OK
    goto :install_deps
)

echo   Poetry nao encontrado. Instalando via pipx...

where pipx >nul 2>&1
if %errorlevel% neq 0 (
    echo   pipx nao encontrado. Instalando pipx...
    python -m pip install --user pipx
    if %errorlevel% neq 0 (
        echo ERRO: Falha ao instalar pipx.
        goto :fail
    )
    python -m pipx ensurepath
    echo.
    echo ATENCAO: O pipx foi instalado e adicionado ao PATH.
    echo Feche este terminal, abra um novo e execute INSTALL.bat novamente.
    goto :fail
)

pipx install poetry
if %errorlevel% neq 0 (
    echo ERRO: Falha ao instalar Poetry via pipx.
    goto :fail
)

where poetry >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo ATENCAO: Poetry foi instalado mas nao esta no PATH atual.
    echo Feche este terminal, abra um novo e execute INSTALL.bat novamente.
    goto :fail
)

echo   Poetry instalado com sucesso. OK
echo.

:: --------------------------------------------------
:: 3. Instalar dependencias do projeto
:: --------------------------------------------------
:install_deps
echo.
echo [3/3] Instalando dependencias do projeto...
echo.

poetry install --only main
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
echo   poetry run backlog-manager
echo.
goto :eof

:fail
echo.
echo Instalacao abortada.
exit /b 1
