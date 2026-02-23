import streamlit as st
import plotly.graph_objects as go
from datetime import datetime

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="JA Eng | Technical Engine", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&family=JetBrains+Mono&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .stMetric { background-color: #f8f9fa; padding: 20px; border-radius: 4px; border: 1px solid #e9ecef; }
    .print-report { background-color: white; padding: 40px; border: 1px solid #ddd; color: #1a1a1a; }
    .memoria-calc { font-family: 'JetBrains Mono', monospace; font-size: 0.85em; background: #f1f3f5; padding: 15px; border-radius: 4px; }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Parâmetros")
    pv = st.number_input("Investimento Inicial (PV)", min_value=0.01, value=50000.0)
    k = st.number_input("Número de Períodos (K)", min_value=1, max_value=50, value=5)
    cf = [st.number_input(f"Fluxo Ano {n}", value=15000.0, key=f"cf_{n}") for n in range(1, k + 1)]

# --- LÓGICA COM LOG DE CONVERGÊNCIA ---
log_convergencia = []
a_sum = sum(cf)
b_sum = sum(v * (i+1) for i, v in enumerate(cf))

try:
    # Estimativa Inicial (Linha 180 do BASIC)
    i1 = (a_sum / pv) ** (a_sum / b_sum) - 1
    log_convergencia.append({"it": 0, "taxa": i1, "erro": 1.0})
    
    # Refinamento (Linhas 200-270)
    for it in range(1, 101):
        pc = sum(v / (1 + i1)**(i+1) for i, v in enumerate(cf))
        t_err = (pc - pv) / pv
        i1 = i1 + t_err / 5
        
        if it <= 5 or abs(t_err) < 0.0001: # Salva as primeiras 5 e a última
            log_convergencia.append({"it": it, "taxa": i1, "erro": t_err})
        
        if abs(t_err) < 0.0001: break
    
    tir_final = int(i1 * 10000 + 0.5) / 100
except:
    tir_final = 0

# --- ABAS ---
tabs = st.tabs(["📊 Dashboard", "📄 Relatório Técnico"])

with tabs[0]:
    c1, c2 = st.columns([1, 2])
    with c1:
        st.metric("TIR CALCULADA", f"{tir_final}%")
        with st.expander("🔍 Ver Memória de Cálculo (Iterações)"):
            for item in log_convergencia:
                st.write(f"Iteração {item['it']}: Taxa={item['taxa']:.6f} | Erro={item['erro']:.6f}")
    with c2:
        fig = go.Figure(data=[
            go.Bar(name='Saída', x=['Inv.'], y=[-pv], marker_color='#d63031'),
            go.Bar(name='Entradas', x=[f'Ano {i+1}' for i in range(k)], y=cf, marker_color='#002b49')
        ])
        fig.update_layout(height=300, margin=dict(l=0,r=0,t=0,b=0), template="plotly_white")
        st.plotly_chart(fig, use_container_width=True)

with tabs[1]:
    st.markdown(f"""
    <div class="print-report">
        <h2 style="color: #002b49;">RELATÓRIO DE ENGENHARIA ECONÔMICA</h2>
        <p><strong>ALGORITMO:</strong> JA & M SOFTWARE 1984 (Newton-Raphson Damped)</p>
        <hr>
        <h4>1. RESUMO DOS INPUTS</h4>
        <ul><li>Investimento: R$ {pv:,.2f}</li><li>Períodos: {k}</li></ul>
        <h4>2. MEMÓRIA DE CÁLCULO (CONVERGÊNCIA)</h4>
        <div class="memoria-calc">
            {"<br>".join([f"PASSO {m['it']}: Taxa Estimada {m['taxa']*100:.4f}% | Erro Relativo: {m['erro']:.6f}" for m in log_convergencia])}
        </div>
        <h3 style="text-align: center; margin-top: 40px; color: #002b49;">TIR FINAL: {tir_final}%</h3>
        <div style="margin-top: 60px; border-top: 1px solid #000; width: 250px; text-align: center;">
            <p>Assinatura Técnica</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
