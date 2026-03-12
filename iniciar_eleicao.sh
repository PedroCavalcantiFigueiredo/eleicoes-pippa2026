#!/bin/bash

# Entra na pasta do script
cd "$(dirname "$0")"

# Verifica se o Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "[ERRO] Python3 não encontrado. Instale com: sudo apt install python3"
    exit 1
fi

# Cria o ambiente virtual se ele não existir
if [ ! -d "venv" ]; then
    echo "Criando ambiente virtual (Venv)..."
    python3 -m venv venv
fi

# Ativa o ambiente virtual
source venv/bin/activate

echo "Verificando dependências..."
# Instala as libs apenas dentro do venv (não afeta o sistema)
pip install streamlit pandas plotly -q

echo ""
echo "Iniciando a Urna Eletrônica..."
echo "Acesse: http://localhost:8501"
echo ""

# Roda o Streamlit de dentro do venv
streamlit run main_V2.0.py

# Se o processo fechar, desativa o venv
deactivate