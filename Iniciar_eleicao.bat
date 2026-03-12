@echo off
title Servidor da Eleicao IPB
color 0A

:: Esse comando abaixo força o Windows a abrir a pasta certa!
cd /d "%~dp0"

echo Verificando se o Python esta instalado...
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERRO FATAL] O Python nao foi encontrado neste computador!
    echo Voce precisa instalar o Python e marcar a caixa "Add Python to PATH" na instalacao.
    echo.
    pause
    exit
)

echo.
echo Preparando o sistema... (Pode demorar uns segundinhos)
pip install streamlit pandas plotly -q

echo.
echo Iniciando a Urna Eletronica... 
echo Se o navegador nao abrir sozinho, acesse: http://localhost:8501
echo.
streamlit run main_V2.0.py

:: Esse pause impede a tela preta de fechar na sua cara se der erro
pause