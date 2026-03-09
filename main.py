import streamlit as st
import pandas as pd
import plotly.express as px
import os
import time
import json
from datetime import datetime

# --- CONFIGURAÇÃO DE CAMINHOS ---
ARQUIVO_CONFIG = "config_eleicao.json"
ARQUIVO_VOTOS = "votos.csv"
NOME_LOGO = "Ipb_logo.png"
PASTA_FOTOS = "fotos"
PASTA_P = os.path.join(PASTA_FOTOS, "presbiteros")
PASTA_D = os.path.join(PASTA_FOTOS, "diaconos")

# Garante que as pastas existam
for p in [PASTA_P, PASTA_D]:
    if not os.path.exists(p):
        os.makedirs(p)

def listar_candidatos_por_pasta():
    """Lê as pastas específicas e retorna as listas de nomes (sem extensão)"""
    p_nomes = [os.path.splitext(f)[0] for f in os.listdir(PASTA_P) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    d_nomes = [os.path.splitext(f)[0] for f in os.listdir(PASTA_D) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    return sorted(p_nomes), sorted(d_nomes)

def carregar_config():
    cand_p, cand_d = listar_candidatos_por_pasta()
    base_config = {"vagas_p": 3, "vagas_d": 4}
    if os.path.exists(ARQUIVO_CONFIG):
        with open(ARQUIVO_CONFIG, "r", encoding="utf-8") as f:
            base_config.update(json.load(f))
    base_config["candidatos_p"] = cand_p
    base_config["candidatos_d"] = cand_d
    return base_config

def salvar_config(vagas_p, vagas_d):
    with open(ARQUIVO_CONFIG, "w", encoding="utf-8") as f:
        json.dump({"vagas_p": vagas_p, "vagas_d": vagas_d}, f, indent=4)

config = carregar_config()

# --- ESTILO CSS (Mantido) ---
st.set_page_config(page_title="Eleição IPB", page_icon="🗳️", layout="wide", initial_sidebar_state="collapsed")
st.markdown("""
    <style>
    [data-testid="collapsedControl"] { display: none; }
    header { visibility: hidden !important; }
    footer { visibility: hidden !important; }
    .block-container { padding-top: 1rem !important; }
    .stApp { background-color: #f2f7f4; }
    h1, h2, h3 { color: #0e4a30 !important; }
    .candidato-nome { text-align: center; font-weight: 900; color: #0e4a30; text-transform: uppercase; margin-bottom: 10px; }
    div.stButton > button[kind="primary"] { background-color: #0e4a30; color: white; border-radius: 8px; }
    div.stButton > button[kind="secondary"] { background-color: #595959; color: white; border-radius: 8px; }
    </style>
""", unsafe_allow_html=True)

def mostrar_cabecalho(titulo=""):
    c1, c2 = st.columns([1, 4])
    with c1:
        if os.path.exists(NOME_LOGO): st.image(NOME_LOGO, width=180)
    with c2:
        if titulo: st.markdown(f"<h1 style='margin-top:20px;'>{titulo}</h1>", unsafe_allow_html=True)

def buscar_foto_candidato(nome, cargo):
    pasta = PASTA_P if cargo == "P" else PASTA_D
    for ext in [".png", ".jpg", ".jpeg"]:
        caminho = os.path.join(pasta, f"{nome}{ext}")
        if os.path.exists(caminho):
            return caminho
    return "https://cdn.pixabay.com/photo/2015/10/05/22/37/blank-profile-picture-973460_960_720.png"

# --- LÓGICA DE ESTADO E NAVEGAÇÃO ---
if 'etapa' not in st.session_state: st.session_state.etapa = 'votacao'
if 'votos_p' not in st.session_state: st.session_state.votos_p = []
if 'votos_d' not in st.session_state: st.session_state.votos_d = []

tela = st.query_params.get("tela", "home")

# --- TELAS: HOME E URNA (Ajustadas para novas pastas) ---
if tela == "home":
    mostrar_cabecalho("Sistema de Eleição IPB")
    st.divider()
    c1, c2, c3 = st.columns(3)
    if c1.button("🗳️ ABRIR URNA", use_container_width=True, type="primary"): st.query_params["tela"] = "urna"; st.rerun()
    if c2.button("📊 RESULTADOS", use_container_width=True, type="primary"): st.query_params["tela"] = "resultados"; st.rerun()
    if c3.button("⚙️ CONFIGURAR", use_container_width=True, type="secondary"): st.query_params["tela"] = "config"; st.rerun()

elif tela == "urna":
    if st.session_state.etapa == 'votacao':
        mostrar_cabecalho("Eleição de Oficiais")
        # Seção Presbíteros
        st.subheader(f"1. Presbíteros (Escolha até {config['vagas_p']})")
        cols = st.columns(6)
        for i, nome in enumerate(config['candidatos_p']):
            with cols[i % 6]:
                with st.container(border=True):
                    st.image(buscar_foto_candidato(nome, "P"), use_container_width=True)
                    st.markdown(f"<p class='candidato-nome'>{nome}</p>", unsafe_allow_html=True)
                    marcado = nome in st.session_state.votos_p
                    if st.button("VOTAR" if not marcado else "✅", key=f"p_{nome}", type="primary" if not marcado else "secondary", use_container_width=True):
                        if marcado: st.session_state.votos_p.remove(nome)
                        elif len(st.session_state.votos_p) < config['vagas_p']: st.session_state.votos_p.append(nome)
                        st.rerun()
        st.divider()
        # Seção Diáconos
        st.subheader(f"2. Diáconos (Escolha até {config['vagas_d']})")
        cols = st.columns(6)
        for i, nome in enumerate(config['candidatos_d']):
            with cols[i % 6]:
                with st.container(border=True):
                    st.image(buscar_foto_candidato(nome, "D"), use_container_width=True)
                    st.markdown(f"<p class='candidato-nome'>{nome}</p>", unsafe_allow_html=True)
                    marcado = nome in st.session_state.votos_d
                    if st.button("VOTAR" if not marcado else "✅", key=f"d_{nome}", type="primary" if not marcado else "secondary", use_container_width=True):
                        if marcado: st.session_state.votos_d.remove(nome)
                        elif len(st.session_state.votos_d) < config['vagas_d']: st.session_state.votos_d.append(nome)
                        st.rerun()
        if st.button("REVISAR VOTOS ➡️", type="primary", use_container_width=True): st.session_state.etapa = 'confirmacao'; st.rerun()

    elif st.session_state.etapa == 'confirmacao':
        mostrar_cabecalho("Confirme sua escolha")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("### Presbíteros:")
            for v in st.session_state.votos_p: st.markdown(f"<h3 style='color:#0e4a30;'>✔️ {v}</h3>", unsafe_allow_html=True)
        with c2:
            st.markdown("### Diáconos:")
            for v in st.session_state.votos_d: st.markdown(f"<h3 style='color:#0e4a30;'>✔️ {v}</h3>", unsafe_allow_html=True)
        col_b1, col_b2 = st.columns(2)
        if col_b1.button("⬅️ CORRIGIR", use_container_width=True): st.session_state.etapa = 'votacao'; st.rerun()
        if col_b2.button("CONFIRMAR VOTO 🔒", type="primary", use_container_width=True):
            # Lógica de salvar votos aqui...
            st.session_state.etapa = 'agradecimento'; st.rerun()

    elif st.session_state.etapa == 'agradecimento':
        st.balloons()
        st.markdown("<h1 style='text-align:center; color:#0e4a30; margin-top:100px;'>VOTO REGISTRADO!</h1>", unsafe_allow_html=True)
        time.sleep(3); st.session_state.votos_p, st.session_state.votos_d, st.session_state.etapa = [], [], 'votacao'; st.rerun()

# --- CONFIGURAÇÃO (Nova lógica de pastas) ---
elif tela == "config":
    mostrar_cabecalho("Configurações")
    
    with st.form("vagas"):
        c1, c2 = st.columns(2)
        v_p = c1.number_input("Vagas Presbítero", value=config['vagas_p'], min_value=1)
        v_d = c2.number_input("Vagas Diácono", value=config['vagas_d'], min_value=1)
        if st.form_submit_button("SALVAR NÚMERO DE VAGAS"):
            salvar_config(v_p, v_d); st.success("Vagas salvas!"); time.sleep(1); st.rerun()

    st.divider()
    st.subheader("📸 Gerenciar Candidatos por Pasta")
    
    col_up1, col_up2 = st.columns(2)
    with col_up1:
        st.info("Upload para **Presbíteros**")
        uplo_p = st.file_uploader("Foto Presbítero", type=["jpg", "png", "jpeg"], key="up_p")
        if uplo_p:
            with open(os.path.join(PASTA_P, uplo_p.name), "wb") as f: f.write(uplo_p.getbuffer())
            st.success(f"{uplo_p.name} salvo em presbiteros!"); time.sleep(1); st.rerun()

    with col_up2:
        st.info("Upload para **Diáconos**")
        uplo_d = st.file_uploader("Foto Diácono", type=["jpg", "png", "jpeg"], key="up_d")
        if uplo_d:
            with open(os.path.join(PASTA_D, uplo_d.name), "wb") as f: f.write(uplo_d.getbuffer())
            st.success(f"{uplo_d.name} salvo em diaconos!"); time.sleep(1); st.rerun()

    st.divider()
    c_list1, c_list2 = st.columns(2)
    c_list1.write(f"**Presbíteros ({len(config['candidatos_p'])}):**")
    c_list1.write(", ".join(config['candidatos_p']) if config['candidatos_p'] else "Nenhum")
    c_list2.write(f"**Diáconos ({len(config['candidatos_d'])}):**")
    c_list2.write(", ".join(config['candidatos_d']) if config['candidatos_d'] else "Nenhum")

    if st.button("🗑️ RESETAR VOTOS"):
        if os.path.exists(ARQUIVO_VOTOS): os.remove(ARQUIVO_VOTOS); st.rerun()
    
    st.button("VOLTAR AO INÍCIO", on_click=lambda: st.query_params.update(tela="home"))