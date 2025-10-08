import streamlit as st
import pandas as pd

st.set_page_config(page_title="Comparador CLT vs PJ", page_icon="💼", layout="centered")

st.title("Simulador: CLT vs PJ")

st.markdown("""
Este simulador estima o **salário equivalente como PJ** a partir de um salário CLT,
considerando benefícios e encargos.  
Preencha os campos abaixo para personalizar sua simulação.
""")

# --- Entradas do usuário ---
st.sidebar.header("Parâmetros de Entrada")

salario_clt = st.sidebar.number_input("Salário bruto CLT (R$)", 0.0, 100000.0, 11100.0, step=500.0)
alimentacao = st.sidebar.number_input("Benefício alimentação (R$)", 0.0, 5000.0, 1100.0, step=100.0)
plano_saude = st.sidebar.number_input("Plano de saúde (R$)", 0.0, 2000.0, 200.0, step=50.0)

contabilidade = st.sidebar.number_input("Custo contabilidade (R$)", 0.0, 2000.0, 500.0, step=50.0)
previdencia = st.sidebar.number_input("Previdência (R$)", 0.0, 2000.0, 300.0, step=50.0)
aliquota_simples = st.sidebar.slider("Alíquota Simples Nacional (%)", 0.0, 30.0, 10.0, step=0.5)

# --- Cálculos ---
# Benefícios CLT (13º + férias + 1/3)
beneficios_anuais = salario_clt + (salario_clt * 1/3) + salario_clt
beneficios_mensais = beneficios_anuais / 12
fgts_mensal = salario_clt * 0.08

# Custo total mensal CLT
custo_total_clt = salario_clt + alimentacao + plano_saude + fgts_mensal + (beneficios_mensais - salario_clt)

# Salário PJ equivalente bruto
salario_pj_equivalente = custo_total_clt + salario_clt

# Custos PJ
simples_nacional = salario_pj_equivalente * (aliquota_simples / 100)
custo_pj = contabilidade + previdencia + simples_nacional
pj_liquido = salario_pj_equivalente - custo_pj


# --- Resultados ---
st.subheader("Resultados da Simulação")

col1, col2 = st.columns(2)

with col1:
    st.metric("Custo total CLT (mensal)", f"R$ {custo_total_clt:,.2f}")
    st.metric("FGTS mensal", f"R$ {fgts_mensal:,.2f}")
    st.metric("Benefícios mensais (13º + férias)", f"R$ {beneficios_mensais - salario_clt:,.2f}")

with col2:
    st.metric("Salário PJ equivalente bruto", f"R$ {salario_pj_equivalente:,.2f}")
    st.metric("Custos PJ", f"R$ {custo_pj:,.2f}")
    st.metric("Salário PJ líquido estimado", f"R$ {pj_liquido:,.2f}")

# --- Comparativo gráfico ---
dados = pd.DataFrame({
    "Categoria": ["Custo CLT", "PJ Líquido"],
    "Valor (R$)": [custo_total_clt, pj_liquido]
})
