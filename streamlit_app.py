import streamlit as st
import plotly.graph_objects as go
from datetime import datetime

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="JA Eng | Simulador de TIR", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&family=JetBrains+Mono&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .onboarding-msg { padding: 20px; border-radius: 8px; background-color: #e7f3ff; border: 1px solid #b2d7ff; color: #004085; margin-bottom: 20px; }
    .stMetric { background-color: #f8f9fa; border: 1px solid #e9ecef; padding: 15px; border-radius: 8px; }
    .audit-box { font-family: 'JetBrains Mono', monospace; font-size: 0.85em; background: #262730; color: #00FF41; padding: 15px; border-radius: 4px; }
    </style>
    """, unsafe_allow_html=True)

# --- INICIALIZAÇÃO DO ESTADO ---
if 'tutorial_concluido' not in st.session_state:
    st.session_state.tutorial_concluido = False
if 'n_fluxos' not in st.session_state:
    st.session_state.n_fluxos = 1

# --- CABEÇALHO ---
st.title("🧮 Simulador de Investimento")
st.caption("Engine de Cálculo JA & M Software | Brasília-DF | Legado 1984")
st.markdown("---")

# --- COLUNAS ---
col_input, col_display = st.columns([1, 2], gap="large")

with col_input:
    st.subheader("Entrada de Dados")
    
    if not st.session_state.tutorial_concluido:
        st.markdown("""
            <div class="onboarding-msg">
                <b>Bem-vindo!</b><br>
                Insira o <b>Valor do Investimento</b> abaixo para destravar o simulador.
            </div>
        """, unsafe_allow_html=True)

    pv = st.number_input("Quanto será investido hoje? (R$)", min_value=0.0, step=1000.0)
    
    if pv > 0:
        if not st.session_state.tutorial_concluido:
            st.toast("Passo 1 concluído! Agora preencha os retornos.", icon="🚀")
            st.session_state.tutorial_concluido = True

        st.write("---")
        st.markdown("**Fluxos de Retorno (Anuais)**")
        
        fluxos = []
        for i in range(st.session_state.n_fluxos):
            valor = st.number_input(f"Ano {i+1} (R$)", min_value=0.0, value=0.0, key=f"cf_{i}")
            fluxos.append(valor)
        
        c1, c2 = st.columns(2)
        with c1:
            if st.button("➕ Adicionar Ano"):
                st.session_state.n_fluxos += 1
                st.rerun()
        with c2:
            if st.button("➖ Remover Ano") and st.session_state.n_fluxos > 1:
                st.session_state.n_fluxos -= 1
                st.rerun()

# --- ÁREA DE RESULTADOS & AUDITORIA ---
with col_display:
    if pv > 0 and any(f > 0 for f in fluxos):
        
        # --- MOTOR DE CÁLCULO (LÓGICA 1984 COM LOG DE AUDITORIA) ---
        log_auditoria = []
        try:
            a_sum = sum(fluxos)
            b_sum = sum(v * (i+1) for i, v in enumerate(fluxos))
            # Estimativa inicial (Linha 180 do BASIC)
            i1 = (a_sum / pv) ** (a_sum / b_sum) - 1
            log_auditoria.append(f"INÍCIO: Estimativa I1 = {i1:.6f}")
            
            for it in range(1, 101):
                pc = sum(v / (1 + i1)**(i+1) for i, v in enumerate(fluxos))
                t_err = (pc - pv) / pv
                i1 = i1 + t_err / 5
                
                # Registra as primeiras iterações para auditoria
                if it <= 5:
                    log_auditoria.append(f"PASSO {it}: Erro {t_err:.6f} -> Nova Taxa: {i1:.6f}")
                
                if abs(t_err) < 0.0001: 
                    log_auditoria.append(f"CONVERGÊNCIA: Erro final {t_err:.8f}")
                    break
            
            tir_final = int(i1 * 10000 + 0.5) / 100
        except:
            tir_final = 0

        tab_dash, tab_relat = st.tabs(["📊 Dashboard", "📄 Relatório & Auditoria"])
        
        with tab_dash:
            st.markdown("### Resumo do Cenário")
            st.metric("Sua Taxa Interna de Retorno (TIR)", f"{tir_final}%")
            
            fig = go.Figure()
            fig.add_trace(go.Bar(x=['Investimento'], y=[-pv], marker_color='#d63031', name='Saída'))
            fig.add_trace(go.Bar(x=[f'Ano {i+1}' for i in range(len(fluxos))], y=fluxos, marker_color='#002b49', name='Entradas'))
            fig.update_layout(height=350, margin=dict(l=0,r=0,t=20,b=0), template="plotly_white", showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
            
            st.info("💡 **Dica:** O Dashboard mostra se o projeto é rentável de forma visual. Para detalhes técnicos, acesse a aba ao lado.")

        with tab_relat:
            st.markdown("### Relatório Técnico e Memória de Cálculo")
            
            # Bloco de Relatório
            st.markdown(f"""
                <div style="background: white; border: 1px solid #ddd; padding: 25px; border-radius: 4px; margin-bottom: 20px;">
                    <h3 style="color: #002b49; margin-top:0;">CERTIFICADO DE CÁLCULO</h3>
                    <p><b>Data do Processamento:</b> {datetime.now().strftime('%d/%m/%Y às %H:%M')}</p>
                    <hr>
                    <p>Investimento Inicial (PV): R$ {pv:,.2f}</p>
                    <p>Fluxos Totais: {len(fluxos)} anos</p>
                    <h2 style="color: #27ae60; text-align: center;">TIR FINAL: {tir_final}%</h2>
                </div>
            """, unsafe_allow_html=True)
            
            # Bloco de Auditoria (Memória de Cálculo)
            with st.expander("🛠️ Auditoria do Algoritmo (Kernel 1984)"):
                st.write("Abaixo está o log de processamento interno do algoritmo original:")
                st.markdown(f"""
                    <div class="audit-box">
                    { "<br>".join(log_auditoria) }
                    </div>
                """, unsafe_allow_html=True)
                st.caption("Nota: O erro deve ser inferior a 0.0001 para garantir a precisão de engenharia.")

            st.button("🖨️ Imprimir Relatório (Ctrl+P)")
            
    else:
        st.subheader("📊 Resultados")
        st.info("Preencha o investimento inicial para ver a mágica acontecer.")
        st.image("https://img.icons8.com/dotty/100/002b49/financial-growth-analysis.png")
