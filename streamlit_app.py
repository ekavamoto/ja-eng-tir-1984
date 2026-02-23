import streamlit as st
import plotly.graph_objects as go
from datetime import datetime

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="JA Eng | Simulador de TIR", layout="wide")

# CSS para estilo Arup e Onboarding
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .onboarding-msg { padding: 20px; border-radius: 8px; background-color: #e7f3ff; border: 1px solid #b2d7ff; color: #004085; margin-bottom: 20px; }
    .stMetric { background-color: #f8f9fa; border: 1px solid #e9ecef; padding: 15px; border-radius: 8px; }
    </style>
    """, unsafe_allow_html=True)

# --- INICIALIZAÇÃO DO ESTADO (Memória do App) ---
if 'tutorial_concluido' not in st.session_state:
    st.session_state.tutorial_concluido = False
if 'n_fluxos' not in st.session_state:
    st.session_state.n_fluxos = 1

# --- CABEÇALHO ---
st.title("🧮 Simulador de Investimento")
st.caption("Tecnologia de Cálculo JA & M Software | Legado 1984")
st.markdown("---")

# --- COLUNAS ---
col_input, col_display = st.columns([1, 2], gap="large")

with col_input:
    st.subheader("Entrada de Dados")
    
    # Se ainda não terminou o tutorial, mostra a mensagem de boas-vindas
    if not st.session_state.tutorial_concluido:
        st.markdown("""
            <div class="onboarding-msg">
                <b>Bem-vindo!</b><br>
                Para começar, insira o <b>Valor do Investimento</b> abaixo. 
                Isso destravará o restante do simulador para você.
            </div>
        """, unsafe_allow_html=True)

    # INPUT PRINCIPAL: Valor Presente
    pv = st.number_input("Quanto será investido hoje? (R$)", min_value=0.0, step=1000.0)
    
    # Lógica de destravamento: Se PV > 0, consideramos que ele começou a usar
    if pv > 0:
        if not st.session_state.tutorial_concluido:
            st.toast("Ótimo! Agora preencha os retornos anuais.", icon="✅")
            st.session_state.tutorial_concluido = True

        st.write("---")
        st.markdown("**Fluxos de Retorno (Anuais)**")
        
        fluxos = []
        for i in range(st.session_state.n_fluxos):
            valor = st.number_input(f"Ano {i+1} (R$)", min_value=0.0, key=f"cf_{i}")
            fluxos.append(valor)
        
        # Controles de períodos
        c1, c2 = st.columns(2)
        with c1:
            if st.button("➕ Adicionar Ano"):
                st.session_state.n_fluxos += 1
                st.rerun()
        with c2:
            if st.button("➖ Remover Ano") and st.session_state.n_fluxos > 1:
                st.session_state.n_fluxos -= 1
                st.rerun()

# --- ÁREA DE RESULTADOS ---
with col_display:
    # Só mostra resultados se houver algum dado inserido
    if pv > 0 and any(f > 0 for f in fluxos):
        
        # CÁLCULO ALGORITMO 1984
        try:
            a_sum = sum(fluxos)
            b_sum = sum(v * (i+1) for i, v in enumerate(fluxos))
            i1 = (a_sum / pv) ** (a_sum / b_sum) - 1
            for _ in range(100):
                pc = sum(v / (1 + i1)**(i+1) for i, v in enumerate(fluxos))
                t_err = (pc - pv) / pv
                if abs(t_err) < 0.0001: break
                i1 = i1 + t_err / 5
            tir_final = int(i1 * 10000 + 0.5) / 100
        except:
            tir_final = 0

        tab_dash, tab_relat = st.tabs(["📊 Dashboard de Análise", "📄 Relatório para Impressão"])
        
        with tab_dash:
            st.markdown("### Resumo do Cenário")
            st.info("Este painel mostra a viabilidade do seu projeto. A TIR representa a rentabilidade anual do investimento.")
            
            st.metric("Taxa Interna de Retorno (TIR)", f"{tir_final}%")
            
            # Gráfico
            fig = go.Figure()
            fig.add_trace(go.Bar(x=['Investimento'], y=[-pv], marker_color='#d63031', name='Saída'))
            fig.add_trace(go.Bar(x=[f'Ano {i+1}' for i in range(len(fluxos))], y=fluxos, marker_color='#002b49', name='Entradas'))
            fig.update_layout(height=350, margin=dict(l=0,r=0,t=20,b=0), template="plotly_white", showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

        with tab_relat:
            st.markdown("### Memorial Técnico")
            st.write("Relatório detalhado contendo a memória de cálculo do algoritmo JA & M.")
            
            st.markdown(f"""
                <div style="background: white; border: 1px solid #ddd; padding: 30px; border-radius: 4px;">
                    <h3 style="color: #002b49; margin-top:0;">RELATÓRIO DE VIABILIDADE</h3>
                    <p><b>Data:</b> {datetime.now().strftime('%d/%m/%Y')}</p>
                    <hr>
                    <p><b>Investimento:</b> R$ {pv:,.2f}</p>
                    <p><b>Fluxos Analisados:</b> {len(fluxos)} anos</p>
                    <h2 style="text-align: center; color: #27ae60;">TIR: {tir_final}%</h2>
                    <br>
                    <p style="font-size: 0.8em; color: gray; border-top: 1px solid #eee; padding-top: 10px;">
                        Cálculo processado via Engine 1984 portado para Python.
                    </p>
                </div>
            """, unsafe_allow_html=True)
            st.caption("Pressione Ctrl + P para salvar este relatório em PDF.")
            
    else:
        # Estado de espera (Vazio)
        st.subheader("Painel de Resultados")
        st.write("Aguardando os dados de investimento para iniciar a projeção...")
        st.image("https://img.icons8.com/dotty/100/002b49/financial-growth-analysis.png")
