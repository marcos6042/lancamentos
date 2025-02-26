
# Importando as bibliotecas necessárias
import streamlit as st
import pandas as pd
import numpy as np

# Função para importar planilha
def importar_planilha():
    st.title("Automação de Lançamentos Contábeis")
    uploaded_file = st.file_uploader("Importe sua planilha financeira (XLSX ou CSV)", type=['xlsx', 'csv'])
    if uploaded_file:
        if uploaded_file.name.endswith('.xlsx'):
            df = pd.read_excel(uploaded_file, engine='openpyxl')
        else:
            df = pd.read_csv(uploaded_file)
        st.dataframe(df.head())
        return df
    return None

# Função para configurar regras de classificação
def configurar_regras(df):
    st.subheader("Configuração de Regras")
    colunas = df.columns.tolist()
    coluna_descricao = st.selectbox("Selecione a coluna de Descrição", colunas)
    coluna_valor = st.selectbox("Selecione a coluna de Valor", colunas)
    
    regras = []
    if st.button("Adicionar Regra"):
        palavra_chave = st.text_input("Palavra-chave para Classificação")
        conta_debito = st.text_input("Conta Débito")
        conta_credito = st.text_input("Conta Crédito")
        if palavra_chave and conta_debito and conta_credito:
            regras.append({
                "palavra_chave": palavra_chave,
                "conta_debito": conta_debito,
                "conta_credito": conta_credito
            })
            st.success("Regra adicionada com sucesso!")
    return coluna_descricao, coluna_valor, regras
