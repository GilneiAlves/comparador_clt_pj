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

