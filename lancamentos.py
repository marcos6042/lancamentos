
import streamlit as st
import pandas as pd
import numpy as np
import hashlib

# Função para hash da senha
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Banco de dados simulado para usuários
usuarios = {'adm': hash_password('adm')}

# Variável de sessão para controle de login
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'current_user' not in st.session_state:
    st.session_state.current_user = None

# Tela de login
def tela_login():
    st.title("Login do Sistema")
    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type='password')
    if st.button("Entrar"):
        if usuario in usuarios and usuarios[usuario] == hash_password(senha):
            st.session_state.logged_in = True
            st.session_state.current_user = usuario
            st.success("Login realizado com sucesso!")
        else:
            st.error("Usuário ou senha inválidos!")
    if st.button("Cadastrar Novo Usuário"):
        st.session_state.logged_in = 'cadastro'

# Tela de cadastro de novo usuário
def tela_cadastro():
    st.title("Cadastro de Novo Usuário")
    novo_usuario = st.text_input("Novo Usuário")
    nova_senha = st.text_input("Nova Senha", type='password')
    if st.button("Cadastrar"):
        if novo_usuario in usuarios:
            st.error("Usuário já existe!")
        else:
            usuarios[novo_usuario] = hash_password(nova_senha)
            st.success("Usuário cadastrado com sucesso!")
            st.session_state.logged_in = False

# Tela de configuração do layout da planilha
def tela_configuracao_layout():
    st.title("Configuração do Layout da Planilha Financeira")
    uploaded_file = st.file_uploader("Importe sua planilha financeira (XLSX ou CSV)", type=['xlsx', 'csv'])
    if uploaded_file:
        if uploaded_file.name.endswith('.xlsx'):
            df = pd.read_excel(uploaded_file, engine='openpyxl')
        else:
            df = pd.read_csv(uploaded_file)
        st.dataframe(df.head())
        colunas = df.columns.tolist()
        st.subheader("Mapeamento das Colunas")
        banco_coluna = st.selectbox("Banco", colunas)
        data_pagamento_coluna = st.selectbox("Data de Pagamento", colunas)
        valor_pago_coluna = st.selectbox("Valor Pago", colunas)
        emitente_coluna = st.selectbox("Emitente", colunas)
        descricao_coluna = st.selectbox("Descrição", colunas)
        banco_transferencia_coluna = st.selectbox("Banco Transferência", colunas)
        entrada_saida_coluna = st.selectbox("Entrada/Saída", colunas)
        plano_contas_rec_coluna = st.selectbox("Plano de Contas REC", colunas)
        observacao1_coluna = st.selectbox("Observação 1", colunas)
        observacao2_coluna = st.selectbox("Observação 2", colunas)
        if st.button("Salvar Configuração"):
            st.success("Configuração salva com sucesso!")

# Tela principal
def tela_principal():
    st.sidebar.title(f"Bem-vindo, {st.session_state.current_user}!")
    menu = st.sidebar.radio("Navegação", ["Configuração do Layout", "Plano de Contas", "Sair"])
    if menu == "Configuração do Layout":
        tela_configuracao_layout()
    elif menu == "Plano de Contas":
        st.title("Plano de Contas")
        plano_de_contas = []
        if 'plano_de_contas' not in st.session_state:
            st.session_state.plano_de_contas = []

        with st.form(key='plano_contas_form'):
            conta = st.text_input("Nome da Conta")
            codigo = st.text_input("Código da Conta")
            adicionar = st.form_submit_button("Adicionar Conta")
            if adicionar and conta and codigo:
                st.session_state.plano_de_contas.append({"codigo": codigo, "conta": conta})
                st.success("Conta adicionada com sucesso!")

        st.subheader("Plano de Contas Cadastrado")
        if st.session_state.plano_de_contas:
            df_plano = pd.DataFrame(st.session_state.plano_de_contas)
            st.dataframe(df_plano)

            # Opção para download do plano de contas
            output_file = "plano_de_contas.xlsx"
            df_plano.to_excel(output_file, index=False)
            with open(output_file, "rb") as file:
                st.download_button(label="Baixar Plano de Contas",
                                   data=file,
                                   file_name=output_file,
                                   mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

            # Opção para excluir conta
            st.subheader("Excluir Conta do Plano de Contas")
            conta_para_excluir = st.selectbox("Selecione a conta para excluir", df_plano['conta'].tolist())
            if st.button("Excluir Conta"):
                st.session_state.plano_de_contas = [c for c in st.session_state.plano_de_contas if c['conta'] != conta_para_excluir]
                st.success("Conta excluída com sucesso!")

    elif menu == "Sair":
        st.session_state.logged_in = False

# Controlador de navegação
if st.session_state.logged_in == False:
    tela_login()
elif st.session_state.logged_in == 'cadastro':
    tela_cadastro()
else:
    tela_principal()
