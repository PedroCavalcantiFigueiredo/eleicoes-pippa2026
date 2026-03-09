import streamlit as st
import pandas as pd
import plotly.express as px
import os
import time
from datetime import datetime

# --- CONFIGURAÇÕES DA IGREJA ---
NOME_LOGO = "Ipb_logo.png" 
VAGAS_PRESBITERO = 3
CANDIDATOS_PRESBITERO = ["Cauã", "Dantas", "PH", "Guido", "Chernobas", "Gabriel Boechat"]

VAGAS_DIACONO = 4
CANDIDATOS_DIACONO = ["Carlos", "André", "Felipe", "Mateus", "Tiago", "Samuel"]

ARQUIVO_VOTOS = "votos.csv"

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
    
    h1, h2, h3 { color: #0e4a30 !important; font-family: 'Arial', sans-serif; }
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
        if os.path.exists(NOME_LOGO):
            st.image(NOME_LOGO, width=200)
        else:
            st.markdown("🏛️ **IPB**")
    with col_titulo:
        if titulo_pagina:
            st.markdown(f"<h1 style='text-align: left; margin-top: 10px;'>{titulo_pagina}</h1>", unsafe_allow_html=True)

def mostrar_foto(nome_candidato):
    p_png = f"fotos/{nome_candidato}.png"
    p_jpg = f"fotos/{nome_candidato}.jpg"
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
    else:
        if len(lista_atual) < limite: lista_atual.append(candidato) 
        else: st.toast(f"⚠️ Máximo de {limite} selecionado!", icon="⚠️")

tela_params = st.query_params.get("tela", "urna") 

# ==========================================
# MODO 1: URNA DE VOTAÇÃO
# ==========================================
if tela_params == "urna":
    if st.session_state.etapa == 'votacao':
        mostrar_cabecalho("Eleição de Oficiais")
        st.divider()
        st.subheader(f"1. Presbíteros (Escolha até {VAGAS_PRESBITERO})")
        colunas_p = st.columns(6)
        for i, candidato in enumerate(CANDIDATOS_PRESBITERO):
            with colunas_p[i % 6]:
                with st.container(border=True):
                    mostrar_foto(candidato)
                    st.markdown(f'<p class="candidato-nome">{candidato}</p>', unsafe_allow_html=True)
                    if candidato in st.session_state.votos_p:
                        if st.button(f"Desmarcar", key=f"p_{candidato}", use_container_width=True): 
                            alternar_voto('votos_p', candidato, VAGAS_PRESBITERO); st.rerun()
                    else:
                        if st.button(f"VOTAR", key=f"p_{candidato}", type="primary", use_container_width=True): 
                            alternar_voto('votos_p', candidato, VAGAS_PRESBITERO); st.rerun()

        st.divider()
        st.subheader(f"2. Diáconos (Escolha até {VAGAS_DIACONO})")
        colunas_d = st.columns(6)
        for i, candidato in enumerate(CANDIDATOS_DIACONO):
            with colunas_d[i % 6]:
                with st.container(border=True):
                    mostrar_foto(candidato)
                    st.markdown(f'<p class="candidato-nome">{candidato}</p>', unsafe_allow_html=True)
                    if candidato in st.session_state.votos_d:
                        if st.button(f"✅ OK", key=f"d_{candidato}", use_container_width=True): 
                            alternar_voto('votos_d', candidato, VAGAS_DIACONO); st.rerun()
                    else:
                        if st.button(f"VOTAR", key=f"d_{candidato}", type="primary", use_container_width=True): 
                            alternar_voto('votos_d', candidato, VAGAS_DIACONO); st.rerun()

        if st.button("➡️ REVISAR MEUS VOTOS", type="primary", use_container_width=True):
            st.session_state.etapa = 'confirmacao'; st.rerun()

    elif st.session_state.etapa == 'confirmacao':
        mostrar_cabecalho("Confirme sua escolha")
        st.divider()
        c1, c2 = st.columns(2)
        with c1: 
            st.subheader("Presbíteros:")
            for v in st.session_state.votos_p: st.success(f"✔️ {v}")
        with c2: 
            st.subheader("Diáconos:")
            for v in st.session_state.votos_d: st.success(f"✔️ {v}")
        st.divider()
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            if st.button("⬅️ CORRIGIR", use_container_width=True): st.session_state.etapa = 'votacao'; st.rerun()
        with col_c2:
            if st.button("CONFIRMAR VOTO 🔒", type="primary", use_container_width=True): 
                salvar_votos(st.session_state.votos_p, st.session_state.votos_d)
                st.session_state.etapa = 'agradecimento'; st.rerun()

    elif st.session_state.etapa == 'agradecimento':
        mostrar_cabecalho()
        st.balloons()
        st.markdown("<h1 style='color: #0e4a30; text-align: center;'>🎉 VOTO REGISTRADO!</h1>", unsafe_allow_html=True)
        st.success("Obrigado por participar.")
        time.sleep(3)
        if st.button("PRÓXIMO ELEITOR", type="primary", use_container_width=True): 
            st.session_state.votos_p = []; st.session_state.votos_d = []; st.session_state.etapa = 'votacao'; st.rerun()

# ==========================================
# MODO 2: TELÃO DE RESULTADOS
# ==========================================
elif tela_params == "resultados":
    col_l, col_t, col_b = st.columns([1, 3, 1])
    with col_l:
        if os.path.exists(NOME_LOGO): st.image(NOME_LOGO, width=200)
    with col_t:
        st.markdown("<h1 style='text-align: left; margin-top: 10px;'>📊 Resultados das eleições</h1>", unsafe_allow_html=True)
    with col_b:
        label = "⬅️ OCULTAR" if st.session_state.mostrar_apuracao else "🏆 APURAR"
        st.write("") 
        if st.button(label, type="primary", use_container_width=True):
            st.session_state.mostrar_apuracao = not st.session_state.mostrar_apuracao
            st.rerun()
    
    st.divider()

    if os.path.exists(ARQUIVO_VOTOS):
        df = pd.read_csv(ARQUIVO_VOTOS)
        c1, c2 = st.columns(2)
        
        with c1:
            st.subheader("Presbíteros")
            df_p = df[df['Cargo'] == 'Presbítero']
            if not df_p.empty:
                cnt_p = df_p['Candidato'].value_counts().reset_index()
                fig_p = px.bar(cnt_p, x='Candidato', y='count', text='count', color_discrete_sequence=['#0e4a30'])
                fig_p.update_layout(plot_bgcolor='white', paper_bgcolor='white', margin=dict(t=30, b=20, l=20, r=20))
                
                # --- ALTERAÇÃO DE CORES (ESCURECIMENTO) ---
                fig_p.update_traces(textposition='outside', textfont=dict(size=14, color='#0e4a30')) # Votos em verde escuro
                fig_p.update_xaxes(tickfont=dict(color="#333333", size=12, family="Arial Black")) # Candidatos em PRETO
                fig_p.update_yaxes(tickfont=dict(color='#333333')) # Números do eixo Y em PRETO
                
                st.plotly_chart(fig_p, use_container_width=True)
        
        with c2:
            st.subheader("Diáconos")
            df_d = df[df['Cargo'] == 'Diácono']
            if not df_d.empty:
                cnt_d = df_d['Candidato'].value_counts().reset_index()
                fig_d = px.bar(cnt_d, x='Candidato', y='count', text='count', color_discrete_sequence=['#595959'])
                fig_d.update_layout(plot_bgcolor='white', paper_bgcolor='white', margin=dict(t=30, b=20, l=20, r=20))
                
                # --- ALTERAÇÃO DE CORES (ESCURECIMENTO) ---
                fig_d.update_traces(textposition='outside', textfont=dict(size=14, color='#333333')) # Votos em cinza escuro
                fig_d.update_xaxes(tickfont=dict(color='#333333', size=12, family="Arial Black")) # Candidatos em PRETO
                fig_d.update_yaxes(tickfont=dict(color='#333333')) # Números do eixo Y em PRETO
                
                st.plotly_chart(fig_d, use_container_width=True)

        if st.session_state.mostrar_apuracao:
            st.divider()
            st.balloons()
            st.markdown("<h1 style='text-align: center;'>🎊 OFICIAIS ELEITOS 🎊</h1>", unsafe_allow_html=True)
            
            st.markdown(f"### {VAGAS_PRESBITERO} Presbíteros Eleitos")
            cp = st.columns(VAGAS_PRESBITERO)
            for i, row in cnt_p.head(VAGAS_PRESBITERO).iterrows():
                with cp[i]: 
                    with st.container(border=True):
                        mostrar_foto(row['Candidato'])
                        st.markdown(f"<p style='text-align:center'><b>{row['Candidato']}</b><br>{row['count']} votos</p>", unsafe_allow_html=True)
            
            st.markdown(f"### {VAGAS_DIACONO} Diáconos Eleitos")
            cd = st.columns(VAGAS_DIACONO)
            for i, row in cnt_d.head(VAGAS_DIACONO).iterrows():
                with cd[i]: 
                    with st.container(border=True):
                        mostrar_foto(row['Candidato'])
                        st.markdown(f"<p style='text-align:center'><b>{row['Candidato']}</b><br>{row['count']} votos</p>", unsafe_allow_html=True)
    
    if not st.session_state.mostrar_apuracao:
        time.sleep(8)
        st.rerun()