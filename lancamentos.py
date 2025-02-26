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
        st.subheader("Pré-visualização da Planilha")
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
    with st.form(key='regras_form'):
        palavra_chave = st.text_input("Palavra-chave para Classificação")
        conta_debito = st.text_input("Conta Débito")
        conta_credito = st.text_input("Conta Crédito")
        adicionar_regra = st.form_submit_button("Adicionar Regra")
        
        if adicionar_regra and palavra_chave and conta_debito and conta_credito:
            regras.append({
                "palavra_chave": palavra_chave,
                "conta_debito": conta_debito,
                "conta_credito": conta_credito
            })
            st.success("Regra adicionada com sucesso!")
    
    # Exibir regras configuradas
    if regras:
        st.subheader("Regras Configuradas")
        for regra in regras:
            st.write(f"Palavra-chave: {regra['palavra_chave']} | Débito: {regra['conta_debito']} | Crédito: {regra['conta_credito']}")
    return coluna_descricao, coluna_valor, regras

# Função para aplicar as regras e classificar lançamentos
def aplicar_regras(df, coluna_descricao, regras):
    st.subheader("Classificação Automática de Lançamentos")
    df['Conta Débito'] = np.nan
    df['Conta Crédito'] = np.nan
    
    for regra in regras:
        mask = df[coluna_descricao].str.contains(regra["palavra_chave"], case=False, na=False)
        df.loc[mask, 'Conta Débito'] = regra["conta_debito"]
        df.loc[mask, 'Conta Crédito'] = regra["conta_credito"]
    
    st.dataframe(df)
    return df

# Função para validar lançamentos contábeis
def validar_lancamentos(df, coluna_valor):
    st.subheader("Validação de Lançamentos Contábeis")
    df['Valor'] = pd.to_numeric(df[coluna_valor], errors='coerce')
    total_debitos = df['Valor'].where(df['Conta Débito'].notna()).sum()
    total_creditos = df['Valor'].where(df['Conta Crédito'].notna()).sum()
    
    st.metric("Total Débitos", f"R$ {total_debitos:,.2f}")
    st.metric("Total Créditos", f"R$ {total_creditos:,.2f}")
    
    if total_debitos != total_creditos:
        st.error("Inconsistência: Total de Débitos é diferente de Créditos!")
    else:
        st.success("Lançamentos contábeis validados com sucesso!")
    return df

# Função para exportar os lançamentos
def exportar_lancamentos(df):
    st.subheader("Exportação de Lançamentos Contábeis")
    output_file = "lancamentos_contabeis.xlsx"
    df.to_excel(output_file, index=False)
    with open(output_file, "rb") as file:
        st.download_button(label="Baixar Lançamentos Contábeis",
                           data=file,
                           file_name=output_file,
                           mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# Estrutura principal do aplicativo
def main():
    st.sidebar.title("Menu de Navegação")
    menu = st.sidebar.radio("Escolha uma opção:", 
                            ["Importar Planilha", "Configurar Regras", "Classificar Lançamentos", "Validar Lançamentos", "Exportar Lançamentos"])

    df = importar_planilha()
    if df is not None:
        coluna_descricao, coluna_valor, regras = configurar_regras(df)
        if regras:
            df = aplicar_regras(df, coluna_descricao, regras)
            df = validar_lancamentos(df, coluna_valor)
            if menu == "Exportar Lançamentos":
                exportar_lancamentos(df)

if __name__ == "__main__":
    main()
