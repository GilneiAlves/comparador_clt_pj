import streamlit as st
import pandas as pd

st.set_page_config(page_title="Comparador CLT vs PJ", page_icon="💼", layout="centered")

st.title("Simulador: CLT vs PJ")

st.markdown("""
Este simulador estima o **salário equivalente como PJ** a partir de um salário CLT,
considerando benefícios e encargos.  
Preencha os campos abaixo para personalizar sua simulação.
""")
