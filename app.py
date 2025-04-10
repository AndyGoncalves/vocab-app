# -*- coding: utf-8 -*-
"""app.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1Xnp3WUzyt1eziRUhnT0rCaeYh_UXxEYv
"""

import streamlit as st
import os
import requests
import json
from bs4 import BeautifulSoup

# Configurações da página
st.set_page_config(page_title="Vocabulário Pessoal", page_icon="📚")

# Verifica/cria diretório de usuários
if not os.path.exists("users"):
    os.makedirs("users")

# Acessa os usuários do secrets
USERS = st.secrets["users"]

def login(username, password):
    return USERS.get(username) == password

def scrape_cambridge(word):
    url = f"https://dictionary.cambridge.org/dictionary/english/{word}"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    try:
        us_entry = soup.find("span", class_="us dpron-i") or soup.find("span", class_="dpron-i")
        ipa_tag = us_entry.find("span", class_="ipa") if us_entry else None
        ipa = ipa_tag.text.strip() if ipa_tag else "N/A"
        audio_tag = us_entry.find("source", {"type": "audio/mpeg"}) if us_entry else None
        audio_url = "https://dictionary.cambridge.org" + audio_tag["src"] if audio_tag else None
        definition_tag = soup.find("div", class_="def ddef_d db")
        definition = definition_tag.text.strip() if definition_tag else "N/A"
        return definition, ipa, audio_url
    except Exception:
        return None, None, None

def save_audio(audio_url, path):
    try:
        audio = requests.get(audio_url)
        with open(path, "wb") as f:
            f.write(audio.content)
        return True
    except:
        return False

def save_word(username, word, frase, definition, ipa, audio_url):
    user_dir = f"users/{username}"
    os.makedirs(user_dir + "/audio", exist_ok=True)
    vocab_path = f"{user_dir}/vocab.json"

    vocab = {}
    if os.path.exists(vocab_path):
        with open(vocab_path, "r", encoding="utf-8") as f:
            vocab = json.load(f)

    vocab[word] = {
        "frase": frase,
        "definition": definition,
        "ipa": ipa,
        "audio_url": audio_url
    }

    with open(vocab_path, "w", encoding="utf-8") as f:
        json.dump(vocab, f, indent=2, ensure_ascii=False)

    if audio_url:
        audio_path = f"{user_dir}/audio/{word}.mp3"
        save_audio(audio_url, audio_path)

def load_vocab(username):
    vocab_path = f"users/{username}/vocab.json"
    if os.path.exists(vocab_path):
        with open(vocab_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

# Sessão de login
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""

# Se o usuário não estiver logado
if not st.session_state.logged_in:
    st.title("🔐 Login")
    username = st.text_input("Usuário")
    password = st.text_input("Senha", type="password")
    
    login_clicked = st.button("Entrar")

    if login_clicked:
        if login(username, password):
            st.session_state.logged_in = True
            st.session_state.username = username
            # Redireciona para a área logada sem mensagens que interrompam o fluxo
            st.experimental_rerun()
        else:
            # Mostra o erro sem tentar reiniciar o app à força
            st.error("Usuário ou senha inválidos.")
else:
    st.title("📘 Meu Vocabulário")
    st.markdown(f"👤 Usuário: `{st.session_state.username}`")

    st.header("➕ Nova palavra")
    word = st.text_input("Palavra em inglês")
    frase = st.text_input("Frase com essa palavra")

    if st.button("Salvar palavra"):
        if word and frase:
            definition, ipa, audio_url = scrape_cambridge(word)
            if definition:
                save_word(st.session_state.username, word, frase, definition, ipa, audio_url)
                st.success(f"Palavra '{word}' salva com sucesso!")
            else:
                st.error("❌ Palavra não encontrada no Cambridge Dictionary.")
        else:
            st.warning("Por favor, preencha todos os campos.")

    st.header("📖 Histórico de palavras salvas")
    vocab = load_vocab(st.session_state.username)

    if not vocab:
        st.info("Você ainda não salvou nenhuma palavra.")
    else:
        for word, data in vocab.items():
            st.subheader(word)
            st.markdown(f"📖 **Definição**: {data.get('definition', 'N/A')}")
            st.markdown(f"🔤 **IPA**: {data.get('ipa', 'N/A')}")
            st.markdown(f"✏️ **Frase**: _{data.get('frase', 'N/A')}_")
    
            audio_url = data.get("audio_url")
            if audio_url:
                st.markdown(f"[🔗 Link para áudio]({audio_url})")
                ext = audio_url.split('.')[-1]
                audio_path = f"users/{st.session_state.username}/audio/{word}.{ext}"
                if os.path.exists(audio_path):
                    with open(audio_path, "rb") as audio_file:
                        audio_bytes = audio_file.read()
                        st.audio(audio_bytes, format=f"audio/{ext}")
                        st.download_button(
                            label="⬇️ Baixar áudio",
                            data=audio_bytes,
                            file_name=f"{word}.{ext}",
                            mime=f"audio/{ext}"
                        )
                else:
                    st.warning("⚠️ Áudio não disponível localmente.")
            else:
                st.warning("⚠️ Nenhum link de áudio disponível.")
