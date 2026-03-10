import streamlit as st
import pandas as pd
import plotly.express as px
import os
import time
import json
from datetime import datetime

# --- CONFIGURAÇÃO DE CAMINHOS E PASTAS ---
ARQUIVO_CONFIG = "config_eleicao.json"
ARQUIVO_VOTOS = "votos.csv"
NOME_LOGO = "Ipb_logo.png"
PASTA_FOTOS = "fotos"
PASTA_P = os.path.join(PASTA_FOTOS, "presbiteros")
PASTA_D = os.path.join(PASTA_FOTOS, "diaconos")

for p in [PASTA_P, PASTA_D]:
    if not os.path.exists(p):
        os.makedirs(p)

def listar_candidatos_por_pasta():
    extensoes = ('.png', '.jpg', '.jpeg')
    p_nomes = [os.path.splitext(f)[0] for f in os.listdir(PASTA_P) if f.lower().endswith(extensoes)]
    d_nomes = [os.path.splitext(f)[0] for f in os.listdir(PASTA_D) if f.lower().endswith(extensoes)]
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

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Eleição IPB", page_icon="🗳️", layout="wide", initial_sidebar_state="collapsed")

# --- ESTILO CSS ---
st.markdown("""
    <style>
    [data-testid="collapsedControl"] { display: none; }
    header { visibility: hidden !important; }
    footer { visibility: hidden !important; }
    .block-container { padding-top: 1rem !important; }
    .stApp { background-color: #f2f7f4; }
    h1, h2, h3 { color: #0e4a30 !important; font-family: 'Arial', sans-serif; }
    [data-testid="stWidgetLabel"] p { color: #0e4a30 !important; font-weight: bold !important; font-size: 16px !important; }
    .candidato-nome { text-align: center; font-weight: 900; color: #0e4a30; text-transform: uppercase; margin: 8px 0; font-size: 15px; }
    div.stButton > button[kind="primary"] { background-color: #0e4a30; color: white; border-radius: 8px; font-weight: bold; }
    div.stButton > button[kind="secondary"] { background-color: #595959; color: white; border-radius: 8px; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

def mostrar_cabecalho(titulo=""):
    c1, c2 = st.columns([1, 4])
    with c1:
        if os.path.exists(NOME_LOGO): st.image(NOME_LOGO, width=200)
        else: st.markdown("🏛️ **IPB**")
    with c2:
        if titulo: st.markdown(f"<h1 style='text-align: left; margin-top: 10px;'>{titulo}</h1>", unsafe_allow_html=True)

def buscar_foto_candidato(nome, cargo):
    pasta = PASTA_P if cargo == "P" else PASTA_D
    for ext in [".png", ".jpg", ".jpeg"]:
        caminho = os.path.join(pasta, f"{nome}{ext}")
        if os.path.exists(caminho): return caminho
    return "https://cdn.pixabay.com/photo/2015/10/05/22/37/blank-profile-picture-973460_960_720.png"

def salvar_votos(p_escolhidos, d_escolhidos):
    novos = []
    agora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    for p in p_escolhidos: novos.append({"DataHora": agora, "Cargo": "Presbítero", "Candidato": p})
    for d in d_escolhidos: novos.append({"DataHora": agora, "Cargo": "Diácono", "Candidato": d})
    df_novo = pd.DataFrame(novos)
    df_novo.to_csv(ARQUIVO_VOTOS, mode='a', index=False, header=not os.path.exists(ARQUIVO_VOTOS))

# --- ESTADOS ---
if 'etapa' not in st.session_state: st.session_state.etapa = 'votacao'
if 'votos_p' not in st.session_state: st.session_state.votos_p = []
if 'votos_d' not in st.session_state: st.session_state.votos_d = []
if 'mostrar_apuracao' not in st.session_state: st.session_state.mostrar_apuracao = False

tela = st.query_params.get("tela", "home")

# ==========================================
# HOME
# ==========================================
if tela == "home":
    mostrar_cabecalho("Sistema de Eleição IPB")
    st.write("---")
    st.markdown("### Selecione uma opção para continuar:")
    c1, c2, c3 = st.columns(3)
    if c1.button("🗳️ ACESSAR URNA", use_container_width=True, type="primary"): st.query_params["tela"] = "urna"; st.rerun()
    if c2.button("📊 VER RESULTADOS", use_container_width=True, type="primary"): st.query_params["tela"] = "resultados"; st.rerun()
    if c3.button("⚙️ CONFIGURAÇÕES", use_container_width=True, type="secondary"): st.query_params["tela"] = "config"; st.rerun()

# ==========================================
# URNA
# ==========================================
elif tela == "urna":
    if st.session_state.etapa == 'votacao':
        mostrar_cabecalho("Eleição de Oficiais")
        st.subheader(f"1. Presbíteros (Escolha até {config['vagas_p']})")
        cols_p = st.columns(6)
        for i, nome in enumerate(config['candidatos_p']):
            with cols_p[i % 6]:
                with st.container(border=True):
                    st.image(buscar_foto_candidato(nome, "P"), use_container_width=True)
                    st.markdown(f'<p class="candidato-nome">{nome}</p>', unsafe_allow_html=True)
                    label = "Desmarcar" if nome in st.session_state.votos_p else "VOTAR"
                    tipo = "secondary" if nome in st.session_state.votos_p else "primary"
                    if st.button(label, key=f"p_{nome}", type=tipo, use_container_width=True):
                        if nome in st.session_state.votos_p: st.session_state.votos_p.remove(nome)
                        elif len(st.session_state.votos_p) < config['vagas_p']: st.session_state.votos_p.append(nome)
                        st.rerun()
        st.divider()
        st.subheader(f"2. Diáconos (Escolha até {config['vagas_d']})")
        cols_d = st.columns(6)
        for i, nome in enumerate(config['candidatos_d']):
            with cols_d[i % 6]:
                with st.container(border=True):
                    st.image(buscar_foto_candidato(nome, "D"), use_container_width=True)
                    st.markdown(f'<p class="candidato-nome">{nome}</p>', unsafe_allow_html=True)
                    label = "Desmarcar" if nome in st.session_state.votos_d else "VOTAR"
                    tipo = "secondary" if nome in st.session_state.votos_d else "primary"
                    if st.button(label, key=f"d_{nome}", type=tipo, use_container_width=True):
                        if nome in st.session_state.votos_d: st.session_state.votos_d.remove(nome)
                        elif len(st.session_state.votos_d) < config['vagas_d']: st.session_state.votos_d.append(nome)
                        st.rerun()
        if st.button("➡️ REVISAR MEUS VOTOS", type="primary", use_container_width=True): st.session_state.etapa = 'confirmacao'; st.rerun()

    elif st.session_state.etapa == 'confirmacao':
        mostrar_cabecalho("Confirme sua escolha")
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("Presbíteros:")
            for v in st.session_state.votos_p: st.markdown(f"<h3 style='color: #0e4a30; margin: 0;'>✔️ {v}</h3>", unsafe_allow_html=True)
        with c2:
            st.subheader("Diáconos:")
            for v in st.session_state.votos_d: st.markdown(f"<h3 style='color: #0e4a30; margin: 0;'>✔️ {v}</h3>", unsafe_allow_html=True)
        
        st.write("")
        cb1, cb2 = st.columns(2)
        if cb1.button("⬅️ CORRIGIR", use_container_width=True): st.session_state.etapa = 'votacao'; st.rerun()
        if cb2.button("CONFIRMAR VOTO 🔒", type="primary", use_container_width=True):
            salvar_votos(st.session_state.votos_p, st.session_state.votos_d)
            st.session_state.etapa = 'agradecimento'; st.rerun()

    elif st.session_state.etapa == 'agradecimento':
        st.balloons()
        st.markdown("<h1 style='text-align:center; color:#0e4a30; margin-top:100px;'>🎉 VOTO REGISTRADO!</h1>", unsafe_allow_html=True)
        time.sleep(3); st.session_state.votos_p, st.session_state.votos_d, st.session_state.etapa = [], [], 'votacao'; st.rerun()

# ==========================================
# RESULTADOS (Como no seu original)
# ==========================================
elif tela == "resultados":
    col_l, col_t, col_b = st.columns([1, 3, 1])
    with col_l:
        if os.path.exists(NOME_LOGO): st.image(NOME_LOGO, width=200)
    with col_t: st.markdown("<h1 style='margin-top: 10px;'>📊 Resultados</h1>", unsafe_allow_html=True)
    with col_b:
        btn_label = "APURAR RESULTADOS" if not st.session_state.mostrar_apuracao else "⬅️ VOLTAR"
        if st.button(btn_label, type="primary"):
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
            st.markdown("<h1 style='text-align: center;'>OFICIAIS ELEITOS</h1>", unsafe_allow_html=True)
            for cargo, vagas, p_ref in zip(["Presbítero", "Diácono"], [config['vagas_p'], config['vagas_d']], ["P", "D"]):
                st.markdown(f"### {vagas} {cargo}s Eleitos")
                df_res = df[df['Cargo'] == cargo]
                if not df_res.empty:
                    cnt = df_res['Candidato'].value_counts().reset_index().head(vagas)
                    cols_ap = st.columns(vagas)
                    for idx, row in cnt.iterrows():
                        with cols_ap[idx]:
                            with st.container(border=True):
                                st.image(buscar_foto_candidato(row['Candidato'], p_ref), use_container_width=True)
                                st.markdown(f"<p style='text-align:center; color:#595959;'><b>{row['Candidato']}</b><br>{row['count']} votos</p>", unsafe_allow_html=True)
    if not st.session_state.mostrar_apuracao:
        time.sleep(8); st.rerun()

# ==========================================
# CONFIGURAÇÕES
# ==========================================
elif tela == "config":
    mostrar_cabecalho("Configurações")
    with st.form("form_vagas"):
        c1, c2 = st.columns(2)
        v_p = c1.number_input("Vagas Presbítero", value=config['vagas_p'], min_value=1)
        v_d = c2.number_input("Vagas Diácono", value=config['vagas_d'], min_value=1)
        if st.form_submit_button("SALVAR"):
            salvar_config(v_p, v_d); st.success("Salvo!"); time.sleep(1); st.rerun()
    st.divider()
    st.subheader("📸 Upload de Fotos")
    up1, up2 = st.columns(2)
    with up1:
        u_p = st.file_uploader("Foto Presbítero", type=["jpg", "png", "jpeg"], key="up_p")
        if u_p:
            with open(os.path.join(PASTA_P, u_p.name), "wb") as f: f.write(u_p.getbuffer())
            st.success("Salvo em Presbíteros!"); time.sleep(1); st.rerun()
    with up2:
        u_d = st.file_uploader("Foto Diácono", type=["jpg", "png", "jpeg"], key="up_d")
        if u_d:
            with open(os.path.join(PASTA_D, u_d.name), "wb") as f: f.write(u_d.getbuffer())
            st.success("Salvo em Diáconos!"); time.sleep(1); st.rerun()
    st.divider()
    if st.button("🗑️ RESETAR VOTOS"):
        if os.path.exists(ARQUIVO_VOTOS): os.remove(ARQUIVO_VOTOS); st.rerun()
    st.button("VOLTAR", on_click=lambda: st.query_params.update(tela="home"))