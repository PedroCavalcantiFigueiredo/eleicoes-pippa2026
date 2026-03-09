import streamlit as st
import pandas as pd
import plotly.express as px
import os
import time
import json
from datetime import datetime

# --- PERSISTÊNCIA DE CONFIGURAÇÕES ---
ARQUIVO_CONFIG = "config_eleicao.json"
ARQUIVO_VOTOS = "votos.csv"
NOME_LOGO = "Ipb_logo.png"

def carregar_config():
    if os.path.exists(ARQUIVO_CONFIG):
        with open(ARQUIVO_CONFIG, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "vagas_p": 3,
        "candidatos_p": ["Cauã", "Dantas", "PH", "Guido", "Chernobas", "Gabriel Boechat"],
        "vagas_d": 4,
        "candidatos_d": ["Carlos", "André", "Felipe", "Mateus", "Tiago", "Samuel"]
    }

def salvar_config(config_dict):
    with open(ARQUIVO_CONFIG, "w", encoding="utf-8") as f:
        json.dump(config_dict, f, ensure_ascii=False, indent=4)

# Inicializa configurações
config = carregar_config()

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Eleição IPB", page_icon="🗳️", layout="wide", initial_sidebar_state="collapsed")

# --- ESTILIZAÇÃO (CSS Personalizado) ---
st.markdown("""
    <style>
    [data-testid="collapsedControl"] { display: none; }
    header { visibility: hidden !important; }
    footer { visibility: hidden !important; }
    .block-container { padding-top: 1rem !important; padding-bottom: 2rem !important; }
    .stApp { background-color: #f2f7f4; }
    
    /* Títulos Principais */
    h1, h2, h3 { color: #0e4a30 !important; font-family: 'Arial', sans-serif; }
    
    /* MUDANÇA AQUI: Cor das Labels (Rótulos dos campos) */
    [data-testid="stWidgetLabel"] p {
        color: #0e4a30 !important; 
        font-weight: bold !important;
        font-size: 16px !important;
    }
    
    .candidato-nome { 
        text-align: center; font-weight: 900; color: #0e4a30; 
        font-size: 15px; margin: 8px 0px 8px 0px; text-transform: uppercase;
    }
    
    div.stButton > button[kind="primary"] { background-color: #0e4a30; color: white; border-radius: 8px; font-weight: bold; }
    div.stButton > button[kind="secondary"] { background-color: #595959; color: white; border-radius: 8px; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

def mostrar_cabecalho(titulo_pagina=""):
    col_logo, col_titulo = st.columns([1, 4])
    with col_logo:
        if os.path.exists(NOME_LOGO): st.image(NOME_LOGO, width=200)
        else: st.markdown("🏛️ **IPB**")
    with col_titulo:
        if titulo_pagina: st.markdown(f"<h1 style='text-align: left; margin-top: 10px;'>{titulo_pagina}</h1>", unsafe_allow_html=True)

def mostrar_foto(nome_candidato):
    p_png, p_jpg = f"fotos/{nome_candidato}.png", f"fotos/{nome_candidato}.jpg"
    if os.path.exists(p_png): st.image(p_png, use_container_width=True)
    elif os.path.exists(p_jpg): st.image(p_jpg, use_container_width=True)
    else: st.image("https://cdn.pixabay.com/photo/2015/10/05/22/37/blank-profile-picture-973460_960_720.png", use_container_width=True)

def salvar_votos(presbiteros_escolhidos, diaconos_escolhidos):
    novos_votos = []
    agora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    for p in presbiteros_escolhidos: novos_votos.append({"DataHora": agora, "Cargo": "Presbítero", "Candidato": p})
    for d in diaconos_escolhidos: novos_votos.append({"DataHora": agora, "Cargo": "Diácono", "Candidato": d})
    df_novo = pd.DataFrame(novos_votos)
    if not os.path.exists(ARQUIVO_VOTOS): df_novo.to_csv(ARQUIVO_VOTOS, index=False)
    else: df_novo.to_csv(ARQUIVO_VOTOS, mode='a', header=False, index=False)

if 'etapa' not in st.session_state: st.session_state.etapa = 'votacao'
if 'votos_p' not in st.session_state: st.session_state.votos_p = []
if 'votos_d' not in st.session_state: st.session_state.votos_d = []
if 'mostrar_apuracao' not in st.session_state: st.session_state.mostrar_apuracao = False

def alternar_voto(cargo, candidato, limite):
    lista_atual = st.session_state[cargo]
    if candidato in lista_atual: lista_atual.remove(candidato) 
    elif len(lista_atual) < limite: lista_atual.append(candidato) 
    else: st.toast(f"⚠️ Máximo de {limite} selecionado!", icon="⚠️")

# Alterado o default para "home"
tela_params = st.query_params.get("tela", "home")

# ==========================================
# PÁGINA INICIAL
# ==========================================
if tela_params == "home":
    mostrar_cabecalho("Sistema de Eleição IPB")
    st.write("---")
    st.markdown("### Selecione uma opção para continuar:")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🗳️ ACESSAR URNA", use_container_width=True, type="primary"):
            st.query_params["tela"] = "urna"
            st.rerun()
            
    with col2:
        if st.button("📊 VER RESULTADOS", use_container_width=True, type="primary"):
            st.query_params["tela"] = "resultados"
            st.rerun()
            
    with col3:
        if st.button("⚙️ CONFIGURAÇÕES", use_container_width=True, type="secondary"):
            st.query_params["tela"] = "config"
            st.rerun()

# ==========================================
# MODO 1: URNA
# ==========================================
elif tela_params == "urna":
    if st.session_state.etapa == 'votacao':
        mostrar_cabecalho("Eleição de Oficiais")
        st.subheader(f"1. Presbíteros (Escolha até {config['vagas_p']})")
        cols_p = st.columns(6)
        for i, cand in enumerate(config['candidatos_p']):
            with cols_p[i % 6]:
                with st.container(border=True):
                    mostrar_foto(cand)
                    st.markdown(f'<p class="candidato-nome">{cand}</p>', unsafe_allow_html=True)
                    label = "Desmarcar" if cand in st.session_state.votos_p else "VOTAR"
                    tipo = "secondary" if cand in st.session_state.votos_p else "primary"
                    if st.button(label, key=f"p_{cand}", type=tipo, use_container_width=True):
                        alternar_voto('votos_p', cand, config['vagas_p']); st.rerun()

        st.divider()
        st.subheader(f"2. Diáconos (Escolha até {config['vagas_d']})")
        cols_d = st.columns(6)
        for i, cand in enumerate(config['candidatos_d']):
            with cols_d[i % 6]:
                with st.container(border=True):
                    mostrar_foto(cand)
                    st.markdown(f'<p class="candidato-nome">{cand}</p>', unsafe_allow_html=True)
                    label = "✅ OK" if cand in st.session_state.votos_d else "VOTAR"
                    tipo = "secondary" if cand in st.session_state.votos_d else "primary"
                    if st.button(label, key=f"d_{cand}", type=tipo, use_container_width=True):
                        alternar_voto('votos_d', cand, config['vagas_d']); st.rerun()

        if st.button("➡️ REVISAR MEUS VOTOS", type="primary", use_container_width=True):
            st.session_state.etapa = 'confirmacao'; st.rerun()

    elif st.session_state.etapa == 'confirmacao':
        mostrar_cabecalho("Confirme sua escolha")
        c1, c2 = st.columns(2)
        with c1: 
            st.subheader("Presbíteros:"); [st.success(f"✔️ {v}") for v in st.session_state.votos_p]
        with c2: 
            st.subheader("Diáconos:"); [st.success(f"✔️ {v}") for v in st.session_state.votos_d]
        col_c1, col_c2 = st.columns(2)
        if col_c1.button("⬅️ CORRIGIR", use_container_width=True): st.session_state.etapa = 'votacao'; st.rerun()
        if col_c2.button("CONFIRMAR VOTO 🔒", type="primary", use_container_width=True):
            salvar_votos(st.session_state.votos_p, st.session_state.votos_d)
            st.session_state.etapa = 'agradecimento'; st.rerun()

    elif st.session_state.etapa == 'agradecimento':
        mostrar_cabecalho()
        st.balloons()
        st.markdown("<h1 style='color: #0e4a30; text-align: center;'>🎉 VOTO REGISTRADO!</h1>", unsafe_allow_html=True)
        time.sleep(3)
        st.session_state.votos_p, st.session_state.votos_d, st.session_state.etapa = [], [], 'votacao'
        st.rerun()

# ==========================================
# MODO 2: RESULTADOS
# ==========================================
elif tela_params == "resultados":
    col_l, col_t, col_b = st.columns([1, 3, 1])
    with col_l:
        if os.path.exists(NOME_LOGO): st.image(NOME_LOGO, width=200)
    with col_t: st.markdown("<h1 style='margin-top: 10px;'>📊 Resultados</h1>", unsafe_allow_html=True)
    with col_b:
        if st.button("🏆 APURAR" if not st.session_state.mostrar_apuracao else "⬅️ VOLTAR", type="primary"):
            st.session_state.mostrar_apuracao = not st.session_state.mostrar_apuracao; st.rerun()
    
    if os.path.exists(ARQUIVO_VOTOS):
        df = pd.read_csv(ARQUIVO_VOTOS)
        c1, c2 = st.columns(2)
        for col, cargo, color in zip([c1, c2], ["Presbítero", "Diácono"], ["#0e4a30", "#595959"]):
            with col:
                st.subheader(cargo + "s")
                df_c = df[df['Cargo'] == cargo]
                if not df_c.empty:
                    cnt = df_c['Candidato'].value_counts().reset_index()
                    fig = px.bar(cnt, x='Candidato', y='count', text='count', color_discrete_sequence=[color])
                    fig.update_layout(plot_bgcolor='white', paper_bgcolor='white', margin=dict(t=30, b=20, l=20, r=20))
                    fig.update_traces(textposition='outside', textfont=dict(size=14, color=color))
                    fig.update_xaxes(tickfont=dict(color="#333333", size=12, family="Arial Black"))
                    st.plotly_chart(fig, use_container_width=True)

        if st.session_state.mostrar_apuracao:
            st.divider()
            st.markdown("<h1 style='text-align: center;'>🎊 OFICIAIS ELEITOS 🎊</h1>", unsafe_allow_html=True)
            for cargo, vagas, df_res in zip(["Presbítero", "Diácono"], [config['vagas_p'], config['vagas_d']], [df[df['Cargo']=='Presbítero'], df[df['Cargo']=='Diácono']]):
                st.markdown(f"### {vagas} {cargo}s Eleitos")
                if not df_res.empty:
                    cnt = df_res['Candidato'].value_counts().reset_index().head(vagas)
                    cols = st.columns(vagas)
                    for idx, row in cnt.iterrows():
                        with cols[idx]:
                            with st.container(border=True):
                                mostrar_foto(row['Candidato'])
                                st.markdown(f"<p style='text-align:center'><b>{row['Candidato']}</b><br>{row['count']} votos</p>", unsafe_allow_html=True)
    if not st.session_state.mostrar_apuracao:
        time.sleep(8); st.rerun()

# ==========================================
# MODO 3: CONFIGURAÇÃO (?tela=config)
# ==========================================
elif tela_params == "config":
    mostrar_cabecalho("Configurações")
    
    with st.form("form_config"):
        col1, col2 = st.columns(2)
        vagas_p = col1.number_input("Vagas Presbítero", value=config['vagas_p'], min_value=1)
        vagas_d = col2.number_input("Vagas Diácono", value=config['vagas_d'], min_value=1)
        
        cand_p = st.text_area("Candidatos Presbítero (um por linha)", value="\n".join(config['candidatos_p']))
        cand_d = st.text_area("Candidatos Diácono (um por linha)", value="\n".join(config['candidatos_d']))
        
        if st.form_submit_button("SALVAR CONFIGURAÇÕES"):
            config['vagas_p'], config['vagas_d'] = vagas_p, vagas_d
            config['candidatos_p'] = [c.strip() for c in cand_p.split("\n") if c.strip()]
            config['candidatos_d'] = [c.strip() for c in cand_d.split("\n") if c.strip()]
            salvar_config(config)
            st.success("Configurações salvas!"); time.sleep(1); st.rerun()

    st.divider()
    st.subheader("📸 Upload de Fotos")
    uplo = st.file_uploader("Selecione a foto (Nome do arquivo = Nome do Candidato)", type=["jpg", "png"])
    if uplo:
        if not os.path.exists("fotos"): os.makedirs("fotos")
        with open(os.path.join("fotos", uplo.name), "wb") as f: f.write(uplo.getbuffer())
        st.success(f"Foto {uplo.name} salva!")

    if st.button("🗑️ RESETAR TODOS OS VOTOS"):
        if os.path.exists(ARQUIVO_VOTOS): os.remove(ARQUIVO_VOTOS); st.error("Votos apagados!"); st.rerun()

    st.markdown(f"[Ir para Urna](?tela=urna)")