#Aplicativo principal em Streamlit com login + vocabulário por aluno
import streamlit as st
import streamlit_authenticator as stauth

# Usuários e senhas
names = ['Maria', 'João']
usernames = ['maria123', 'joao456']
passwords = ['senha1', 'senha2']

# Hash das senhas
hashed_passwords = stauth.Hasher(passwords).generate()

# Autenticador
authenticator = stauth.Authenticate(names, usernames, hashed_passwords,
                                    'vocab_app', 'abcdef', cookie_expiry_days=1)

# Login
name, authentication_status, username = authenticator.login('Login', 'main')

if authentication_status:
    authenticator.logout('Logout', 'sidebar')
    st.success(f'Bem-vinda(o), {name}!')
    st.write(f'📁 Acessando conteúdo exclusivo de {name}')

    filepath = f"data/{username}_vocab.txt"
    try:
        with open(filepath, "r") as f:
            words = f.readlines()
            st.markdown("### 🧾 Sua lista de vocabulário:")
            for word in words:
                st.write(f"🔹 {word.strip()}")
    except FileNotFoundError:
        st.warning("Nenhuma lista de vocabulário encontrada.")

elif authentication_status == False:
    st.error("Usuário ou senha incorretos.")
elif authentication_status == None:
    st.warning("Digite seu usuário e senha.")
