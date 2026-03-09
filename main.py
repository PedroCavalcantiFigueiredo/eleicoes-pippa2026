import streamlit as st
import pandas as pd
import plotly.express as px
import os
import time
from datetime import datetime

# --- CONFIGURAÇÕES DA IGREJA ---
VAGAS_PRESBITERO = 3
CANDIDATOS_PRESBITERO = ["João Silva", "Pedro Alves", "Marcos Paulo", "Lucas Souza", "Fábio Gomes", "Paulo Roberto"]

VAGAS_DIACONO = 4
CANDIDATOS_DIACONO = ["Carlos", "André", "Felipe", "Mateus", "Tiago", "Samuel"]

ARQUIVO_VOTOS = "votos.csv"

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Eleição IPB", page_icon="🗳️", layout="wide", initial_sidebar_state="collapsed")

# --- ESTILIZAÇÃO (CSS Personalizado) ---
st.markdown("""
    <style>
    /* Esconde elementos nativos do Streamlit para modo Kiosk */
    [data-testid="collapsedControl"] { display: none; } /* Esconde a setinha */
    header { visibility: hidden !important; } /* Esconde cabeçalho */
    footer { visibility: hidden !important; } /* Esconde rodapé */
    .block-container { padding-top: 1rem !important; padding-bottom: 2rem !important; }
    
    /* Cores e Fundos */
    .stApp { background-color: #f2f7f4; }
    h1, h2, h3 { color: #0e4a30 !important; font-family: 'Arial', sans-serif; }
    hr { border-color: #595959 !important; opacity: 0.3; margin: 1.5em 0px; }
    [data-testid="stVerticalBlock"] { gap: 0.5rem !important; }
    
    /* Estilo do Nome do Candidato */
    .candidato-nome { 
        text-align: center; font-weight: 900; color: #0e4a30; 
        font-size: 15px; margin: 8px 0px 8px 0px; text-transform: uppercase;
    }
    
    /* Cores dos Botões */
    div.stButton > button[kind="primary"] {
        background-color: #0e4a30; color: white; border-radius: 8px; border: none; font-weight: bold;
    }
    div.stButton > button[kind="primary"]:hover { background-color: #1a6b48; color: white; }
    
    div.stButton > button[kind="secondary"] {
        background-color: #595959; color: white; border-radius: 8px; border: none; font-weight: bold;
    }
    div.stButton > button[kind="secondary"]:hover { background-color: #3b3b3b; color: white; }
    
    div[data-testid="stAlert"] { background-color: #ffffff; border-left-color: #0e4a30; color: #0e4a30; }
    </style>
""", unsafe_allow_html=True)

# --- FUNÇÃO PARA SALVAR VOTOS ---
def salvar_votos(presbiteros_escolhidos, diaconos_escolhidos):
    novos_votos = []
    agora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    for p in presbiteros_escolhidos: novos_votos.append({"DataHora": agora, "Cargo": "Presbítero", "Candidato": p})
    for d in diaconos_escolhidos: novos_votos.append({"DataHora": agora, "Cargo": "Diácono", "Candidato": d})
        
    df_novo = pd.DataFrame(novos_votos)
    if not os.path.exists(ARQUIVO_VOTOS): df_novo.to_csv(ARQUIVO_VOTOS, index=False)
    else: df_novo.to_csv(ARQUIVO_VOTOS, mode='a', header=False, index=False)

# --- CONTROLE DE ESTADO ---
if 'etapa' not in st.session_state: st.session_state.etapa = 'votacao'
if 'votos_p' not in st.session_state: st.session_state.votos_p = []
if 'votos_d' not in st.session_state: st.session_state.votos_d = []
if 'mostrar_apuracao' not in st.session_state: st.session_state.mostrar_apuracao = False

def alternar_voto(cargo, candidato, limite):
    lista_atual = st.session_state[cargo]
    if candidato in lista_atual: lista_atual.remove(candidato) 
    else:
        if len(lista_atual) < limite: lista_atual.append(candidato) 
        else: st.toast(f"⚠️ Atenção: Você já escolheu o máximo de {limite} candidatos!", icon="⚠️")

# --- ROTEAMENTO ---
query_params = st.query_params
tela_atual = query_params.get("tela", "urna") 

# ==========================================
# MODO 1: URNA DE VOTAÇÃO
# ==========================================
if tela_atual == "urna":
    if st.session_state.etapa == 'votacao':
        col_logo, col_titulo = st.columns([1, 8])
        with col_logo: st.image("https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEiIqA9ae39u_KHbkoFNLU9xWETe8cSfIIEznaC5N5QvfvE2r5MeXFlsKVxFgVSGqNB3jU_Rxsxdd_vGqZ5kKwSf780lIn1jKUqaX2BqOF5_QCSyVKVzwXrlQ7Kzdz8Yo-98aiLvrnO1kMY/s1600/NovaLogoIPB.png", width=150)
        with col_titulo: st.title("🗳️ Eleição de Oficiais")
        st.info("Pressione no botão verde abaixo da foto para selecionar o candidato.")
        
        # --- PRESBÍTEROS ---
        st.subheader(f"1. Presbíteros (Escolha até {VAGAS_PRESBITERO})")
        st.write(f"Você selecionou: **{len(st.session_state.votos_p)} de {VAGAS_PRESBITERO}**")
        colunas_p = st.columns(6)
        for i, candidato in enumerate(CANDIDATOS_PRESBITERO):
            with colunas_p[i % 6]:
                with st.container(border=True):
                    caminho_foto = f"fotos/{candidato}.jpg"
                    if os.path.exists(caminho_foto): st.image(caminho_foto, use_container_width=True)
                    else: st.image("https://cdn.pixabay.com/photo/2015/10/05/22/37/blank-profile-picture-973460_960_720.png", use_container_width=True)
                    st.markdown(f'<p class="candidato-nome">{candidato}</p>', unsafe_allow_html=True)
                    if candidato in st.session_state.votos_p:
                        if st.button(f"✅ DESMARCAR", key=f"p_des_{candidato}", use_container_width=True): alternar_voto('votos_p', candidato, VAGAS_PRESBITERO); st.rerun()
                    else:
                        if st.button(f"VOTAR", key=f"p_vot_{candidato}", type="primary", use_container_width=True): alternar_voto('votos_p', candidato, VAGAS_PRESBITERO); st.rerun()

        st.divider()
        # --- DIÁCONOS ---
        st.subheader(f"2. Diáconos (Escolha até {VAGAS_DIACONO})")
        st.write(f"Você selecionou: **{len(st.session_state.votos_d)} de {VAGAS_DIACONO}**")
        colunas_d = st.columns(6)
        for i, candidato in enumerate(CANDIDATOS_DIACONO):
            with colunas_d[i % 6]:
                with st.container(border=True):
                    caminho_foto = f"fotos/{candidato}.jpg"
                    if os.path.exists(caminho_foto): st.image(caminho_foto, use_container_width=True)
                    else: st.image("https://cdn.pixabay.com/photo/2015/10/05/22/37/blank-profile-picture-973460_960_720.png", use_container_width=True)
                    st.markdown(f'<p class="candidato-nome">{candidato}</p>', unsafe_allow_html=True)
                    if candidato in st.session_state.votos_d:
                        if st.button(f"✅ DESMARCAR", key=f"d_des_{candidato}", use_container_width=True): alternar_voto('votos_d', candidato, VAGAS_DIACONO); st.rerun()
                    else:
                        if st.button(f"VOTAR", key=f"d_vot_{candidato}", type="primary", use_container_width=True): alternar_voto('votos_d', candidato, VAGAS_DIACONO); st.rerun()

        st.divider()
        if st.button("➡️ AVANÇAR PARA REVISÃO DO VOTO", type="primary", use_container_width=True):
            if not st.session_state.votos_p and not st.session_state.votos_d: st.error("Por favor, selecione pelo menos um candidato antes de avançar!")
            else: st.session_state.etapa = 'confirmacao'; st.rerun()

    # --- TELA DE CONFIRMAÇÃO E AGRADECIMENTO ---
    elif st.session_state.etapa == 'confirmacao':
        st.title("⚠️ Revise os seus votos")
        st.info("Verifique se os nomes abaixo estão corretos. Se estiver tudo certo, aperte CONFIRMAR.")
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Para Presbítero:")
            if st.session_state.votos_p: 
                for nome in st.session_state.votos_p: st.success(f"✔️ **{nome}**")
            else: st.warning("Nenhum selecionado (Voto em Branco)")
        with col2:
            st.subheader("Para Diácono:")
            if st.session_state.votos_d: 
                for nome in st.session_state.votos_d: st.success(f"✔️ **{nome}**")
            else: st.warning("Nenhum selecionado (Voto em Branco)")
        st.divider()
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("⬅️ CORRIGIR", use_container_width=True): st.session_state.etapa = 'votacao'; st.rerun()
        with col_btn2:
            if st.button("🔒 CONFIRMAR MEU VOTO", type="primary", use_container_width=True): salvar_votos(st.session_state.votos_p, st.session_state.votos_d); st.session_state.etapa = 'agradecimento'; st.rerun()

    elif st.session_state.etapa == 'agradecimento':
        st.title("🎉 Voto Computado!")
        st.success("Obrigado por participar! Seu voto foi registrado com sucesso.")
        st.balloons()
        st.divider()
        st.write("*(Aguarde o mesário preparar a urna para o próximo membro)*")
        if st.button("Mesário: Reiniciar Urna para o Próximo Membro", use_container_width=True):
            st.session_state.votos_p = []; st.session_state.votos_d = []; st.session_state.etapa = 'votacao'; st.rerun()

# ==========================================
# MODO 2: TELÃO DE RESULTADOS E APURAÇÃO
# ==========================================
elif tela_atual == "resultados":
    
    if not st.session_state.mostrar_apuracao:
        # --- TELA 2.A: GRÁFICOS AO VIVO ---
        col_titulo, col_botao = st.columns([3, 1])
        with col_titulo:
            st.title("📊 Resultados da Eleição IPB")
            st.caption("🔄 Esta tela está no modo automático. Atualizando a cada 8 segundos...")
        with col_botao:
            st.write("") # Espaçamento
            if st.button("APURAR RESULTADOS FINAIS", type="primary", use_container_width=True):
                st.session_state.mostrar_apuracao = True
                st.rerun()
                
        st.divider()
        
        if not os.path.exists(ARQUIVO_VOTOS): 
            st.info("Aguardando votos...")
            time.sleep(8)
            st.rerun()
        else:
            df = pd.read_csv(ARQUIVO_VOTOS)
            col_graf1, col_graf2 = st.columns(2)
            
            with col_graf1:
                st.subheader("Resultado - Presbíteros")
                df_p = df[df['Cargo'] == 'Presbítero']
                if not df_p.empty:
                    contagem_p = df_p['Candidato'].value_counts().reset_index()
                    contagem_p.columns = ['Candidato', 'Votos']
                    contagem_p['Rotulo'] = contagem_p['Votos'].astype(str) + '<br>' + contagem_p['Candidato']
                    fig_p = px.bar(contagem_p, x='Candidato', y='Votos', text='Rotulo', color_discrete_sequence=['#0e4a30'])
                    fig_p.update_traces(textposition='outside', textfont_size=15, textfont_weight="bold", textfont_color="#0e4a30")
                    fig_p.update_layout(xaxis_title="", yaxis_title="", xaxis=dict(showticklabels=False), yaxis=dict(showticklabels=False, range=[0, contagem_p['Votos'].max() * 1.3]), plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', margin=dict(t=30, b=10))
                    st.plotly_chart(fig_p, use_container_width=True)
                    
            with col_graf2:
                st.subheader("Resultado - Diáconos")
                df_d = df[df['Cargo'] == 'Diácono']
                if not df_d.empty:
                    contagem_d = df_d['Candidato'].value_counts().reset_index()
                    contagem_d.columns = ['Candidato', 'Votos']
                    contagem_d['Rotulo'] = contagem_d['Votos'].astype(str) + '<br>' + contagem_d['Candidato']
                    fig_d = px.bar(contagem_d, x='Candidato', y='Votos', text='Rotulo', color_discrete_sequence=['#595959'])
                    fig_d.update_traces(textposition='outside', textfont_size=15, textfont_weight="bold", textfont_color="#595959")
                    fig_d.update_layout(xaxis_title="", yaxis_title="", xaxis=dict(showticklabels=False), yaxis=dict(showticklabels=False, range=[0, contagem_d['Votos'].max() * 1.3]), plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', margin=dict(t=30, b=10))
                    st.plotly_chart(fig_d, use_container_width=True)

        # Atualiza a página magicamente após 8 segundos (só entra aqui se NÃO estiver apurando)
        time.sleep(8)
        st.rerun()

    else:
        # --- TELA 2.B: APURAÇÃO (OS ELEITOS) ---
        st.balloons() # Festa no telão!
        
        col_titulo, col_botao = st.columns([3, 1])
        with col_titulo:
            st.title("🎉 Oficiais Eleitos")
            st.caption("Estes são os candidatos mais votados conforme o número de vagas estipulado.")
        with col_botao:
            st.write("")
            if st.button("⬅️ Voltar aos Gráficos", use_container_width=True):
                st.session_state.mostrar_apuracao = False
                st.rerun()
                
        st.divider()

        if not os.path.exists(ARQUIVO_VOTOS):
            st.warning("Nenhum voto registrado ainda.")
        else:
            df = pd.read_csv(ARQUIVO_VOTOS)
            
            # --- ELEITOS: PRESBÍTEROS ---
            st.markdown(f"<h3 style='text-align: center; color: #0e4a30;'>{VAGAS_PRESBITERO} Presbíteros Eleitos</h3>", unsafe_allow_html=True)
            st.write("")
            df_p = df[df['Cargo'] == 'Presbítero']
            if not df_p.empty:
                contagem_p = df_p['Candidato'].value_counts().reset_index()
                contagem_p.columns = ['Candidato', 'Votos']
                eleitos_p = contagem_p.head(VAGAS_PRESBITERO)
                
                cols_p = st.columns(len(eleitos_p))
                for idx, row in eleitos_p.iterrows():
                    candidato = row['Candidato']
                    votos = row['Votos']
                    with cols_p[idx]:
                        with st.container(border=True):
                            caminho_foto = f"fotos/{candidato}.jpg"
                            if os.path.exists(caminho_foto): st.image(caminho_foto, use_container_width=True)
                            else: st.image("https://cdn.pixabay.com/photo/2015/10/05/22/37/blank-profile-picture-973460_960_720.png", use_container_width=True)
                            st.markdown(f'<p class="candidato-nome">{candidato}</p>', unsafe_allow_html=True)
                            st.markdown(f"<div style='background-color: #0e4a30; color: white; text-align: center; padding: 5px; border-radius: 5px; font-weight: bold;'>{votos} votos</div>", unsafe_allow_html=True)
            else:
                st.write("Sem votos para Presbítero.")

            st.divider()

            # --- ELEITOS: DIÁCONOS ---
            st.markdown(f"<h3 style='text-align: center; color: #595959;'>{VAGAS_DIACONO} Diáconos Eleitos</h3>", unsafe_allow_html=True)
            st.write("")
            df_d = df[df['Cargo'] == 'Diácono']
            if not df_d.empty:
                contagem_d = df_d['Candidato'].value_counts().reset_index()
                contagem_d.columns = ['Candidato', 'Votos']
                eleitos_d = contagem_d.head(VAGAS_DIACONO)
                
                cols_d = st.columns(len(eleitos_d))
                for idx, row in eleitos_d.iterrows():
                    candidato = row['Candidato']
                    votos = row['Votos']
                    with cols_d[idx]:
                        with st.container(border=True):
                            caminho_foto = f"fotos/{candidato}.jpg"
                            if os.path.exists(caminho_foto): st.image(caminho_foto, use_container_width=True)
                            else: st.image("https://cdn.pixabay.com/photo/2015/10/05/22/37/blank-profile-picture-973460_960_720.png", use_container_width=True)
                            
                            st.markdown(f'<p class="candidato-nome" style="color: #595959;">{candidato}</p>', unsafe_allow_html=True)
                            st.markdown(f"<div style='background-color: #595959; color: white; text-align: center; padding: 5px; border-radius: 5px; font-weight: bold;'>{votos} votos</div>", unsafe_allow_html=True)
            else:
                st.write("Sem votos para Diácono.")