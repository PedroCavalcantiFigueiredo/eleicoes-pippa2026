import streamlit as st
import pandas as pd
import plotly.express as px
import os
import time
import json
import uuid
import base64
from datetime import datetime

# --- CONFIGURAÇÃO DE CAMINHOS E PASTAS ---
ARQUIVO_CONFIG = "config_eleicao.json"
ARQUIVO_VOTOS = "votos.csv"
ARQUIVO_LOG = "log_apuracao.txt"
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
st.set_page_config(page_title="Eleição PIPPA 2026", page_icon="🗳️", layout="wide", initial_sidebar_state="collapsed")

# --- ESTILO CSS ---
st.markdown("""
    <style>
    [data-testid="collapsedControl"] { display: none; }
    header { visibility: hidden !important; }
    footer { visibility: hidden !important; }
    .block-container { padding-top: 1rem !important; }
    .stApp { background-color: #f2f7f4; }
    h1, h2, h3 { color: #0e4a30 !important; font-family: 'Arial', sans-serif; }
    
    /* Design dos Cards (Mudança 6) */
    [data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 12px !important;
        background-color: #ffffff;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        border: 1px solid #e0e0e0 !important;
        overflow: hidden;
    }
    
    /* Design e Tamanho dos Botões - Remoção de Bordas (Mudanças 3 e 7) */
    div.stButton > button {
        height: 50px;
        font-size: 16px !important;
        border: none !important;
        transition: 0.2s ease-in-out;
    }
    div.stButton > button:focus, div.stButton > button:active {
        outline: none !important;
        box-shadow: none !important;
        border: none !important;
        color: white !important;
    }
    div.stButton > button[kind="primary"] { background-color: #0e4a30; color: white; border-radius: 8px; font-weight: bold; }
    div.stButton > button[kind="secondary"] { background-color: #8fa89b; color: white; border-radius: 8px; font-weight: bold; }
    div.stButton > button[kind="secondary"]:hover { background-color: #d17575; color: white; }
    
    .candidato-nome { text-align: center; font-weight: 900; color: #0e4a30; text-transform: uppercase; margin: 8px 0; font-size: 15px; }
    </style>
""", unsafe_allow_html=True)

def get_base64_image(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return ""

def mostrar_cabecalho(titulo=""):
    # Mudança 4: Header com fundo diferente
    logo_b64 = get_base64_image(NOME_LOGO)
    img_tag = f'<img src="data:image/png;base64,{logo_b64}" width="150" style="margin-right: 20px;">' if logo_b64 else '<span style="font-size:30px; margin-right:20px;">Primeira Igreja Presbiteriana de Pouso Alegre</span>'
    
    st.markdown(f"""
        <div style="background-color: #d1e2d8; padding: 15px 30px; border-radius: 12px; display: flex; align-items: center; margin-bottom: 25px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
            {img_tag}
            <h1 style="margin: 0; color: #0e4a30; flex-grow: 1;">{titulo}</h1>
        </div>
    """, unsafe_allow_html=True)

def buscar_foto_candidato(nome, cargo):
    pasta = PASTA_P if cargo == "P" else PASTA_D
    for ext in [".png", ".jpg", ".jpeg"]:
        caminho = os.path.join(pasta, f"{nome}{ext}")
        if os.path.exists(caminho): return caminho
    return "https://cdn.pixabay.com/photo/2015/10/05/22/37/blank-profile-picture-973460_960_720.png"

def salvar_votos(p_escolhidos, d_escolhidos):
    novos = []
    agora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    id_eleitor = str(uuid.uuid4())[:8] # Mudança 1: Identificador único por pessoa/envio
    
    for p in p_escolhidos: novos.append({"ID_Eleitor": id_eleitor, "DataHora": agora, "Cargo": "Presbítero", "Candidato": p})
    for d in d_escolhidos: novos.append({"ID_Eleitor": id_eleitor, "DataHora": agora, "Cargo": "Diácono", "Candidato": d})
    
    df_novo = pd.DataFrame(novos)
    df_novo.to_csv(ARQUIVO_VOTOS, mode='a', index=False, header=not os.path.exists(ARQUIVO_VOTOS))

def registrar_log_apuracao(total_eleitores, quorum_necessario, eleitos_p, eleitos_d):
    # Mudança 8: Log histórico de apurações
    agora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    with open(ARQUIVO_LOG, "a", encoding="utf-8") as f:
        f.write(f"[{agora}] APURAÇÃO REALIZADA\n")
        f.write(f"Total de Eleitores: {total_eleitores} | Quórum p/ Eleição (50%+1): {quorum_necessario}\n")
        f.write(f" -> Presbíteros Eleitos: {', '.join(eleitos_p) if eleitos_p else 'Nenhum atingiu o quórum'}\n")
        f.write(f" -> Diáconos Eleitos: {', '.join(eleitos_d) if eleitos_d else 'Nenhum atingiu o quórum'}\n")
        f.write("-" * 50 + "\n")

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
    mostrar_cabecalho("Sistema de Eleição PIPPA 2026")
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
        
        # Mudança 5: Separação das votações com divs de fundo diferente
        st.markdown(f"<div style='background-color: #c4d9cc; padding: 10px 20px; border-radius: 8px; margin-bottom: 15px;'><h3 style='margin:0; color:#0e4a30;'>1. Presbíteros (Escolha até {config['vagas_p']})</h3></div>", unsafe_allow_html=True)
        cols_p = st.columns(6)
        for i, nome in enumerate(config['candidatos_p']):
            with cols_p[i % 6]:
                with st.container(border=True): # O CSS transforma isso em um card (Mudança 6)
                    st.image(buscar_foto_candidato(nome, "P"), use_container_width=True)
                    st.markdown(f'<p class="candidato-nome">{nome}</p>', unsafe_allow_html=True)
                    label = "Desmarcar" if nome in st.session_state.votos_p else "VOTAR"
                    tipo = "secondary" if nome in st.session_state.votos_p else "primary"
                    if st.button(label, key=f"p_{nome}", type=tipo, use_container_width=True):
                        if nome in st.session_state.votos_p: st.session_state.votos_p.remove(nome)
                        elif len(st.session_state.votos_p) < config['vagas_p']: st.session_state.votos_p.append(nome)
                        st.rerun()
                        
        st.write("")
        st.markdown(f"<div style='background-color: #e2e8e4; padding: 10px 20px; border-radius: 8px; margin-bottom: 15px; margin-top: 20px;'><h3 style='margin:0; color:#595959;'>2. Diáconos (Escolha até {config['vagas_d']})</h3></div>", unsafe_allow_html=True)
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
                        
        st.write("---")
        if st.button("➡️ REVISAR MEUS VOTOS", type="primary", use_container_width=True): st.session_state.etapa = 'confirmacao'; st.rerun()

    elif st.session_state.etapa == 'confirmacao':
        mostrar_cabecalho("Confirme sua escolha")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("<div style='background-color: #c4d9cc; padding: 10px; border-radius: 8px;'><h3>Presbíteros:</h3></div>", unsafe_allow_html=True)
            for v in st.session_state.votos_p: st.markdown(f"<h4 style='color: #0e4a30; margin: 10px 0;'>✔️ {v}</h4>", unsafe_allow_html=True)
        with c2:
            st.markdown("<div style='background-color: #e2e8e4; padding: 10px; border-radius: 8px;'><h3>Diáconos:</h3></div>", unsafe_allow_html=True)
            for v in st.session_state.votos_d: st.markdown(f"<h4 style='color: #0e4a30; margin: 10px 0;'>✔️ {v}</h4>", unsafe_allow_html=True)
        
        st.write("")
        cb1, cb2 = st.columns(2)
        if cb1.button("⬅️ CORRIGIR", use_container_width=True): st.session_state.etapa = 'votacao'; st.rerun()
        if cb2.button("CONFIRMAR VOTO 🔒", type="primary", use_container_width=True):
            salvar_votos(st.session_state.votos_p, st.session_state.votos_d)
            st.session_state.etapa = 'agradecimento'; st.rerun()

    elif st.session_state.etapa == 'agradecimento':
        st.balloons()
        st.markdown("<h1 style='text-align:center; color:#0e4a30; margin-top:100px;'>🎉 VOTO REGISTRADO COM SUCESSO!</h1>", unsafe_allow_html=True)
        time.sleep(3); st.session_state.votos_p, st.session_state.votos_d, st.session_state.etapa = [], [], 'votacao'; st.rerun()

# ==========================================
# RESULTADOS
# ==========================================
elif tela == "resultados":
    mostrar_cabecalho("Resultados da Eleição - PIPPA 2026")
    
    col_vazia, col_btn = st.columns([3, 1])
    with col_btn:
        btn_label = "APURAR RESULTADOS" if not st.session_state.mostrar_apuracao else "⬅️ VOLTAR"
        if st.button(btn_label, type="primary", use_container_width=True):
            st.session_state.mostrar_apuracao = not st.session_state.mostrar_apuracao
            st.rerun()
    
    if os.path.exists(ARQUIVO_VOTOS):
        df = pd.read_csv(ARQUIVO_VOTOS)
        
        # Mudança 1 e 2: Lógica de 50% + 1 pessoa
        if 'ID_Eleitor' in df.columns:
            total_eleitores = df['ID_Eleitor'].nunique()
        else:
            total_eleitores = 0 # Fallback caso o CSV seja antigo sem a coluna
            
        quorum_necessario = (total_eleitores // 2) + 1
        
        st.info(f"**Estatísticas:** {total_eleitores} pessoas votaram até o momento. **Quórum para eleição (50%+1):** {quorum_necessario} votos.")
        
        c1, c2 = st.columns(2)
        for col, cargo, color in zip([c1, c2], ["Presbítero", "Diácono"], ["#0e4a30", "#595959"]):
            with col:
                st.markdown(f"### Votos - {cargo}s")
                df_c = df[df['Cargo'] == cargo]
                if not df_c.empty:
                    cnt = df_c['Candidato'].value_counts().reset_index()
                    fig = px.bar(cnt, x='Candidato', y='count', text='count', color_discrete_sequence=[color])
                    fig.update_layout(plot_bgcolor='white', paper_bgcolor='white', margin=dict(t=30, b=20, l=20, r=20))
                    fig.update_traces(textposition='outside', textfont=dict(size=14, color=color))
                    fig.update_xaxes(tickfont=dict(color="#333333", size=12, family="Arial Black"))
                    # Adiciona linha de quórum no gráfico
                    fig.add_hline(y=quorum_necessario, line_dash="dash", line_color="red", annotation_text="50%+1")
                    st.plotly_chart(fig, use_container_width=True)

        if st.session_state.mostrar_apuracao:
            st.divider()
            st.markdown("<div style='background-color: white; color: white; padding: 15px; border-radius: 10px; text-align: center;'><h1 style='color: white; !important; margin: 0;'>OFICIAIS ELEITOS</h1></div>", unsafe_allow_html=True)
            
            eleitos_historico_p = []
            eleitos_historico_d = []

            for cargo, vagas, p_ref in zip(["Presbítero", "Diácono"], [config['vagas_p'], config['vagas_d']], ["P", "D"]):
                st.markdown(f"### {cargo}s (Vagas: {vagas})")
                df_res = df[df['Cargo'] == cargo]
                if not df_res.empty:
                    # Aplica a regra do quórum de 50%+1
                    cnt = df_res['Candidato'].value_counts().reset_index()
                    cnt_eleitos = cnt[cnt['count'] >= quorum_necessario].head(vagas)
                    
                    if cnt_eleitos.empty:
                        st.warning(f"Nenhum candidato a {cargo} alcançou o quórum necessário ({quorum_necessario} votos).")
                    else:
                        cols_ap = st.columns(vagas)
                        for idx, row in cnt_eleitos.iterrows():
                            if p_ref == "P": eleitos_historico_p.append(row['Candidato'])
                            if p_ref == "D": eleitos_historico_d.append(row['Candidato'])
                            with cols_ap[idx]:
                                with st.container(border=True):
                                    st.image(buscar_foto_candidato(row['Candidato'], p_ref), use_container_width=True)
                                    st.markdown(f"<p style='text-align:center; color:#595959; font-size: 18px;'><b>{row['Candidato']}</b><br><span style='color: #0e4a30;'>{row['count']} votos</span></p>", unsafe_allow_html=True)
            
            # Registrar no log automaticamente (Mudança 8)
            registrar_log_apuracao(total_eleitores, quorum_necessario, eleitos_historico_p, eleitos_historico_d)
            st.success(f"Apuração registrada no histórico (`{ARQUIVO_LOG}`).")

    if not st.session_state.mostrar_apuracao:
        time.sleep(8); st.rerun()

# ==========================================
# CONFIGURAÇÕES
# ==========================================
elif tela == "config":
    mostrar_cabecalho("Configurações do Sistema")
    with st.form("form_vagas"):
        c1, c2 = st.columns(2)
        v_p = c1.number_input("Vagas Presbítero", value=config['vagas_p'], min_value=1)
        v_d = c2.number_input("Vagas Diácono", value=config['vagas_d'], min_value=1)
        if st.form_submit_button("SALVAR VAGAS"):
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
    
    st.subheader("⚠️ Área de Perigo")
    c_del1, c_del2 = st.columns(2)
    if c_del1.button("🗑️ RESETAR VOTOS", type="primary"):
        if os.path.exists(ARQUIVO_VOTOS): os.remove(ARQUIVO_VOTOS); st.rerun()
    if c_del2.button("🗑️ LIMPAR LOG DE APURAÇÃO"):
        if os.path.exists(ARQUIVO_LOG): os.remove(ARQUIVO_LOG); st.rerun()
        
    st.write("---")
    st.button("⬅️ VOLTAR PARA HOME", on_click=lambda: st.query_params.update(tela="home"), use_container_width=True)