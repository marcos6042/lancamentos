
# app.py
import streamlit as st
import pandas as pd
import json
import os

# Configuração inicial do App
st.set_page_config(page_title="Automação de Lançamentos Contábeis", layout="wide")
st.title("Automação de Lançamentos Contábeis")

# Diretórios
regras_dir = 'regras'
if not os.path.exists(regras_dir):
    os.makedirs(regras_dir)

# Função para carregar regras salvas
def carregar_regras():
    caminho = os.path.join(regras_dir, 'regras_classificacao.json')
    if os.path.exists(caminho):
        with open(caminho, 'r') as f:
            return json.load(f)
    return {}

# Função para salvar regras
def salvar_regras(regras):
    caminho = os.path.join(regras_dir, 'regras_classificacao.json')
    with open(caminho, 'w') as f:
        json.dump(regras, f, indent=4)

# Função para classificar lançamentos
def classificar_lancamentos(movimento, regras, plano_de_contas):
    lancamentos = []
    for _, linha in movimento.iterrows():
        for regra, conta in regras.items():
            if regra in linha.values:
                valor = linha['Valor']
                historico = linha['Histórico']
                data = linha['Data']
                entrada_saida = linha['Entrada/Saída']
                
                # Débito e Crédito
                if entrada_saida == 'E':
                    debito = conta
                    credito = plano_de_contas[plano_de_contas['Descrição'].str.contains("Banco")]['Código'].values[0]
                else:
                    credito = conta
                    debito = plano_de_contas[plano_de_contas['Descrição'].str.contains("Banco")]['Código'].values[0]
                
                lancamento = {
                    'Data': data,
                    'Histórico': historico,
                    'Valor': valor,
                    'Débito': debito,
                    'Crédito': credito
                }
                lancamentos.append(lancamento)
    return pd.DataFrame(lancamentos)

# Upload do Plano de Contas com tratamento de codificação
st.sidebar.subheader("Importar Plano de Contas")
uploaded_plano = st.sidebar.file_uploader("Escolha o arquivo do Plano de Contas (CSV)", type=['csv'])
if uploaded_plano:
    try:
        plano_de_contas = pd.read_csv(uploaded_plano, delimiter=';', encoding='utf-8')
    except UnicodeDecodeError:
        st.warning("Erro ao ler o arquivo com codificação UTF-8. Tentando com ISO-8859-1.")
        uploaded_plano.seek(0)  # Resetando o ponteiro do arquivo
        plano_de_contas = pd.read_csv(uploaded_plano, delimiter=';', encoding='ISO-8859-1')
    
    st.sidebar.success("Plano de Contas importado com sucesso!")
    st.dataframe(plano_de_contas)

# Upload do Movimento Financeiro
st.sidebar.subheader("Importar Movimento Financeiro")
uploaded_movimento = st.sidebar.file_uploader("Escolha o arquivo de Movimento Financeiro (XLSX)", type=['xlsx'])
if uploaded_movimento:
    movimento_financeiro = pd.read_excel(uploaded_movimento)
    st.sidebar.success("Movimento Financeiro importado com sucesso!")

# Configuração de Layout e Regras
st.subheader("Configuração de Regras de Classificação")
regras_salvas = carregar_regras()

if uploaded_movimento:
    colunas = movimento_financeiro.columns.tolist()
    st.write("Selecione quais colunas servirão como regra de classificação:")
    col_regras = st.multiselect("Escolha as colunas", colunas)

    regras = {}
    for coluna in col_regras:
        unique_vals = movimento_financeiro[coluna].unique()
        for val in unique_vals:
            conta_contabil = st.selectbox(f"Conta Contábil para '{val}' em '{coluna}':", plano_de_contas['Código'].tolist())
            if conta_contabil:
                regras[val] = conta_contabil

    if st.button("Salvar Configuração"):
        salvar_regras(regras)
        st.success("Configuração salva com sucesso!")

# Classificação de Lançamentos
st.subheader("Classificação de Lançamentos")
if uploaded_movimento and uploaded_plano:
    movimento_financeiro['Data'] = pd.to_datetime(movimento_financeiro['Data'], dayfirst=True)
    lancamentos_classificados = classificar_lancamentos(movimento_financeiro, regras_salvas, plano_de_contas)
    st.dataframe(lancamentos_classificados)

    if not lancamentos_classificados.empty:
        st.subheader("Exportar Lançamentos Contábeis")
        if st.button("Exportar para Excel"):
            lancamentos_classificados.to_excel("lancamentos_classificados.xlsx", index=False)
            st.success("Arquivo exportado com sucesso! Baixe o arquivo abaixo:")
            with open("lancamentos_classificados.xlsx", "rb") as file:
                st.download_button(label="Baixar Lançamentos Classificados", data=file, file_name="lancamentos_classificados.xlsx")
