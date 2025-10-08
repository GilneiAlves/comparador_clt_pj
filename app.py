import streamlit as st
import pandas as pd
import altair as alt
import plotly.graph_objects as go
# --- Funções de Cálculo de Impostos ---

def calcular_inss(salario_bruto):
    """Calcula o desconto do INSS de forma progressiva para 2025."""
    teto_inss = 8157.41
    if salario_bruto > teto_inss:
        salario_bruto = teto_inss

    desconto_total = 0
    
    # Faixa 1: 7.5%
    if salario_bruto > 0:
        base_faixa = min(salario_bruto, 1518.00)
        desconto_total += base_faixa * 0.075

    # Faixa 2: 9%
    if salario_bruto > 1518.00:
        base_faixa = min(salario_bruto, 2793.88) - 1518.00
        desconto_total += base_faixa * 0.09

    # Faixa 3: 12%
    if salario_bruto > 2793.88:
        base_faixa = min(salario_bruto, 4190.83) - 2793.88
        desconto_total += base_faixa * 0.12

    # Faixa 4: 14%
    if salario_bruto > 4190.83:
        base_faixa = min(salario_bruto, teto_inss) - 4190.83
        desconto_total += base_faixa * 0.14
        
    # O desconto máximo do INSS em 2025 é R$ 951,62
    return min(desconto_total, 951.62)


def calcular_irrf(salario_bruto, desconto_inss, num_dependentes):
    """Calcula o desconto do IRRF para 2025, considerando dependentes."""
    deducao_por_dependente = 189.59
    deducao_total_dependentes = num_dependentes * deducao_por_dependente
    
    base_calculo = salario_bruto - desconto_inss - deducao_total_dependentes

    if base_calculo <= 2259.20:
        return 0.0
    elif base_calculo <= 2826.65:
        return (base_calculo * 0.075) - 169.44
    elif base_calculo <= 3751.05:
        return (base_calculo * 0.15) - 381.44
    elif base_calculo <= 4664.68:
        return (base_calculo * 0.225) - 662.77
    else:
        return (base_calculo * 0.275) - 896.00

# --- Configuração da Página ---
st.set_page_config(page_title="Comparador CLT vs PJ", page_icon="💼", layout="centered")

st.title("Simulador: CLT vs PJ")

st.markdown("""
Este simulador estima o **salário equivalente como PJ** a partir de um salário CLT,
considerando benefícios e encargos de forma mais precisa.
Preencha os campos ao lado para personalizar sua simulação.
""")

# --- Entradas do usuário ---
st.sidebar.header("Parâmetros de Entrada CLT")

salario_clt = st.sidebar.number_input("Salário bruto CLT (R$)", 0.0, 100000.0, 10000.0, step=100.0)
alimentacao = st.sidebar.number_input("Benefício alimentação (R$)", 0.0, 5000.0, 1000.0, step=100.0)
plano_saude = st.sidebar.number_input("Plano de saúde (R$)", 0.0, 2000.0, 200.0, step=50.0)
num_dependentes = st.sidebar.number_input("Número de dependentes", 0, 20, 0, step=1)


st.sidebar.header("Custos como PJ")
contabilidade = st.sidebar.number_input("Custo contabilidade (R$)", 0.0, 2000.0, 500.0, step=50.0)
previdencia_pj = st.sidebar.number_input("Previdência Privada (PJ, opcional) (R$)", 0.0, 2000.0, 300.0, step=50.0)
aliquota_simples = st.sidebar.slider("Alíquota Simples Nacional (%)", 0.0, 30.0, 10.0, step=0.5)


# --- Cálculos CLT ---
# Descontos
desconto_inss = calcular_inss(salario_clt)
desconto_irrf = calcular_irrf(salario_clt, desconto_inss, num_dependentes)
descontos_clt_total = desconto_inss + desconto_irrf

# Salário Líquido
salario_clt_liquido = salario_clt - descontos_clt_total
salario_clt_liquido_com_beneficios = salario_clt_liquido + alimentacao + plano_saude

# Encargos e Benefícios anuais pagos pelo empregador
decimo_terceiro = salario_clt
ferias = salario_clt
terco_ferias = ferias / 3
fgts_anual = (salario_clt * 12) * 0.08

# Custo total anual para a empresa
custo_anual_clt = (salario_clt * 12) + (alimentacao * 12) + (plano_saude * 12) + decimo_terceiro + ferias + terco_ferias + fgts_anual

# Custo mensal para a empresa (base para o salário PJ)
custo_mensal_clt_para_empresa = custo_anual_clt / 12


# --- Cálculos PJ ---
# O salário PJ bruto deve cobrir o custo que a empresa tinha com o CLT
salario_pj_bruto_equivalente = custo_mensal_clt_para_empresa

# Custos do PJ
imposto_simples = salario_pj_bruto_equivalente * (aliquota_simples / 100)
custos_pj_total = contabilidade + previdencia_pj + imposto_simples
salario_pj_liquido = salario_pj_bruto_equivalente - custos_pj_total


# --- Resultados ---
st.subheader("Resultados da Simulação")

col1, col2 = st.columns(2)

with col1:
    st.metric("Salário Bruto CLT", f"R$ {salario_clt:,.2f}")
    st.markdown(f"(-) INSS: R$ {desconto_inss:,.2f}")
    st.markdown(f"(-) IRRF: R$ {desconto_irrf:,.2f}")
    st.metric("Salário CLT Líquido + Benefícios", f"R$ {salario_clt_liquido_com_beneficios:,.2f}", delta_color="off")
    #st.metric("Custo Total Mensal para a Empresa", f"R$ {custo_mensal_clt_para_empresa:,.2f}")


with col2:
    st.metric("Salário PJ Bruto Equivalente", f"R$ {salario_pj_bruto_equivalente:,.2f}")
    st.markdown(f"(-) Imposto Simples: R$ {imposto_simples:,.2f}")
    st.markdown(f"(-) Outros Custos: R$ {contabilidade + previdencia_pj:,.2f}")
    st.metric("Salário PJ Líquido Estimado", f"R$ {salario_pj_liquido:,.2f}", delta_color="off")


# --- Comparativo gráfico ---
st.subheader("Comparativo de Ganhos Líquidos Mensais")
dados = pd.DataFrame({
    "Categoria": ["CLT Líquido + Benefícios", "PJ Líquido"],
    "Valor (R$)": [salario_clt_liquido_com_beneficios, salario_pj_liquido]
})


fig = go.Figure()

# Adiciona as barras
fig.add_trace(go.Bar(
    x=dados["Categoria"],
    y=dados["Valor (R$)"],
    text=[f"R$ {v:,.2f}" for v in dados["Valor (R$)"]],
    textposition='outside',   # Exibe o rótulo acima das barras
    marker_color=['#1f77b4', '#2ca02c'],  # cores personalizadas (CLT e PJ)
    hovertemplate='%{x}<br><b>R$ %{y:,.2f}</b><extra></extra>',
))

y_max = dados["Valor (R$)"].max() + 3500
# Layout geral
fig.update_layout(
    title={
        'text': ' Comparativo de Modalidades de Contratação',
        'x': 0.5,
        'xanchor': 'center',
        'font': {'size': 20}
    },
    xaxis_title='Modalidade de Contratação',
    yaxis_title='Valor Líquido Mensal (R$)',
        yaxis=dict(
        showgrid=False,
        range=[0, y_max]  # adiciona a margem
    ),
    xaxis=dict(showgrid=False),
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    font=dict(size=14),
)

st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.caption("Desenvolvido em Python + Streamlit por Gilnei Alves de Freitas")
st.markdown("[linkedin-Gilnei](https://www.linkedin.com/in/gilnei-freitas/ )")
