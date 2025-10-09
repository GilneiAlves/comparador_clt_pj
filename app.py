import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- Constantes para o cálculo avançado do PJ ---
LIMITE_MEI_MENSAL = 6750.00
# Limite mensal simbólico para a regra de cálculo. Ajuste se necessário.
LIMITE_SIMPLES_MENSAL = 30000.00 

# --- Funções de Cálculo de Impostos (sem alteração) ---
def calcular_inss(salario_bruto):
    """Calcula o desconto do INSS de forma progressiva para 2025."""
    teto_inss = 8157.41
    if salario_bruto > teto_inss:
        salario_bruto = teto_inss
    desconto_total = 0
    if salario_bruto > 0:
        base_faixa = min(salario_bruto, 1518.00)
        desconto_total += base_faixa * 0.075
    if salario_bruto > 1518.00:
        base_faixa = min(salario_bruto, 2793.88) - 1518.00
        desconto_total += base_faixa * 0.09
    if salario_bruto > 2793.88:
        base_faixa = min(salario_bruto, 4190.83) - 2793.88
        desconto_total += base_faixa * 0.12
    if salario_bruto > 4190.83:
        base_faixa = min(salario_bruto, teto_inss) - 4190.83
        desconto_total += base_faixa * 0.14
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
st.set_page_config(page_title="Comparador CLT vs PJ", page_icon="💼", layout="wide")
st.title("Simulador: CLT vs PJ")
# (Seu markdown de introdução permanece o mesmo)
st.markdown("""
Este simulador calcula e compara o **valor líquido mensal estimado** entre contratação **CLT e PJ**.

Os cálculos consideram:
- **Salário bruto CLT**, com descontos de **INSS** e **IRRF** conforme as faixas vigentes de 2025.  
- **13º salário**, **férias + 1/3** e **FGTS (8%)**, incorporados ao custo mensal da empresa.  
- **Benefícios CLT** como alimentação e plano de saúde.  
- **Custos do PJ**, incluindo **contabilidade**, **Simples Nacional**, **previdência privada** e **custos de deslocamento**.  

O objetivo é estimar quanto uma empresa gastaria para manter um colaborador CLT e qual seria o **salário PJ bruto equivalente** para igualar esse custo — além de exibir o **valor líquido final** em cada modalidade.

Use os controles na barra lateral para personalizar a simulação conforme seu cenário.

*Esta aplicação está em constante aprimoramento.*  
Em breve serão incluídos novos parâmetros e cenários para uma simulação ainda mais precisa.
""")

# --- Entradas do usuário ---
st.sidebar.header("Parâmetros de Entrada CLT")
salario_clt = st.sidebar.number_input("Salário bruto CLT (R$)", 0.0, 100000.0, 1500.0, step=100.0)
alimentacao = st.sidebar.number_input("Benefício alimentação (R$)", 0.0, 5000.0, 1100.0, step=100.0)
plano_saude = st.sidebar.number_input("Plano de saúde (R$)", 0.0, 2000.0, 250.0, step=50.0)
num_dependentes = st.sidebar.number_input("Número de dependentes", 0, 20, 0, step=1)
transporte_clt = st.sidebar.number_input("Custo deslocamento CLT (R$)", 0.0, 2000.0, 800.0, step=50.0)

st.sidebar.header("Custos como PJ")
contabilidade = st.sidebar.number_input("Custo contabilidade (R$)", 0.0, 2000.0, 500.0, step=50.0)
previdencia_pj = st.sidebar.number_input("Previdência Privada (PJ, opcional) (R$)", 0.0, 2000.0, 300.0, step=50.0)
transporte_pj = st.sidebar.number_input("Custo deslocamento PJ (R$)", 0.0, 2000.0, 800.0, step=50.0)
aliquota_simples = st.sidebar.slider("Alíquota Simples Nacional (%)", 0.0, 30.0, 6.0, 0.5)

# --- Cálculos CLT ---
desconto_inss = calcular_inss(salario_clt)
desconto_irrf = calcular_irrf(salario_clt, desconto_inss, num_dependentes)
descontos_clt_total = desconto_inss + desconto_irrf

# Remuneração Líquida Efetiva CLT (Valor Alvo para o PJ)
salario_clt_liquido_com_beneficios = salario_clt - descontos_clt_total + alimentacao + plano_saude - transporte_clt

# --- INÍCIO DA NOVA LÓGICA DE CÁLCULO PJ ---

# 1. Encargos CLT que viram "custo de oportunidade" para o PJ
decimo_terceiro_mensal = salario_clt / 12
terco_ferias_mensal = (salario_clt / 3) / 12
fgts_mensal = salario_clt * 0.08

# 2. Soma de todos os custos que o PJ terá que arcar
custos_clt_perdidos = (decimo_terceiro_mensal + terco_ferias_mensal + fgts_mensal + 
                       alimentacao + plano_saude)
novos_custos_pj = contabilidade + previdencia_pj + transporte_pj

# Soma total dos custos que o PJ assume (equivalente a SUM(D6:D17) da planilha)
soma_custos_pj = custos_clt_perdidos + novos_custos_pj

# 3. Implementação da fórmula do Excel para achar o Salário PJ Mínimo
aliquota = aliquota_simples / 100.0
redutor = 0.65
liquido_alvo = salario_clt_liquido_com_beneficios # O líquido que queremos alcançar

# Fórmula principal (parte 1)
salario_pj_teorico = (liquido_alvo - soma_custos_pj) / (1 - aliquota)

# Lógica condicional (IF)
if salario_pj_teorico >= LIMITE_SIMPLES_MENSAL:
    salario_pj_bruto_equivalente = salario_pj_teorico
else:
    denominador_ajustado = (1 - aliquota * redutor)
    if denominador_ajustado > 0:
        salario_pj_bruto_equivalente = ((liquido_alvo - soma_custos_pj) / denominador_ajustado) + (LIMITE_MEI_MENSAL / denominador_ajustado)
    else:
        salario_pj_bruto_equivalente = 0 # Evita divisão por zero

# 4. Cálculo do líquido final do PJ com base no salário bruto encontrado
imposto_simples = salario_pj_bruto_equivalente * aliquota
salario_pj_liquido = salario_pj_bruto_equivalente - soma_custos_pj - imposto_simples

# --- FIM DA NOVA LÓGICA DE CÁLCULO PJ ---


# --- Resultados ---
st.subheader("Resultados da Simulação")
col1, col2 = st.columns(2)

with col1:
    st.metric("Salário Bruto CLT", f"R$ {salario_clt:,.2f}")
    st.markdown(f"(-) INSS: R$ {desconto_inss:,.2f}")
    st.markdown(f"(-) IRRF: R$ {desconto_irrf:,.2f}")
    st.markdown(f"(-) Deslocamento: R$ {transporte_clt:,.2f}")
    st.markdown(f"**Total Descontos:** R$ {transporte_clt + desconto_irrf + desconto_inss:,.2f}")
    st.metric("Salário CLT Líquido Final (com benefícios)", f"R$ {salario_clt_liquido_com_beneficios:,.2f}", delta_color="off")
    st.metric("Estimativa Anual Líquida CLT", f"R$ {salario_clt_liquido_com_beneficios * 12:,.2f}", delta_color="off")

with col2:
    st.metric("Salário PJ Bruto Mínimo Equivalente", f"R$ {salario_pj_bruto_equivalente:,.2f}")
    st.markdown(f"(-) Imposto Simples ({aliquota_simples}%): R$ {imposto_simples:,.2f}")
    st.markdown(f"(-) Custos Totais Assumidos pelo PJ: R$ {soma_custos_pj:,.2f}")
    st.metric("Salário PJ Líquido Estimado", f"R$ {salario_pj_liquido:,.2f}", 
              delta=f"{salario_pj_liquido - salario_clt_liquido_com_beneficios:,.2f} vs CLT",
              help="A diferença para o líquido CLT ocorre por arredondamentos. O objetivo é que seja próximo de zero.")
    st.metric("Estimativa Anual Líquida PJ", f"R$ {salario_pj_liquido * 12:,.2f}", delta_color="off")

# --- Comparativo gráfico
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
    textposition='outside',
    marker_color=['#1f77b4', '#2ca02c'],
    hovertemplate='%{x}<b>R$ %{y:,.2f}</b><extra></extra>',
))

# Ajuste dinâmico do eixo Y para garantir que o rótulo não seja cortado
y_max = dados["Valor (R$)"].max() * 1.25 

# Layout geral
fig.update_layout(
    title={
        'text': 'Comparativo de Modalidades de Contratação',
        'x': 0.5,
        'xanchor': 'center',
        'font': {'size': 20}
    },
    xaxis_title='Modalidade de Contratação',
    yaxis_title='Valor Líquido Mensal (R$)',
    yaxis=dict(
        showgrid=False,
        range=[0, y_max]  # Adiciona a margem superior
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
