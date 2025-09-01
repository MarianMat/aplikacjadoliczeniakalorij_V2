import streamlit as st
import pandas as pd
import os

# Nazwa pliku z danymi użytkowników
USERS_FILE = "users.csv"

# Wczytywanie danych użytkowników
def load_users():
    if not os.path.exists(USERS_FILE):
        df = pd.DataFrame([
            {"username": "admin", "password": "password123", "role": "admin"},
            {"username": "demo", "password": "demo", "role": "user"}
        ])
        df.to_csv(USERS_FILE, index=False)
    return pd.read_csv(USERS_FILE)

# Uwierzytelnienie
def authenticate(username, password):
    df = load_users()
    user = df[(df["username"] == username) & (df["password"] == password)]
    if not user.empty:
        return user.iloc[0]
    return None

# Interfejs logowania
st.set_page_config(page_title="Logowanie", layout="centered")
st.title("Logowanie do Dziennika Kalorii 🍽️")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.role = None

if not st.session_state.logged_in:
    username = st.text_input("Nazwa użytkownika")
    password = st.text_input("Hasło", type="password")

    if st.button("Zaloguj"):
        user = authenticate(username, password)
        if user is not None:
            st.session_state.logged_in = True
            st.session_state.username = user["username"]
            st.session_state.role = user["role"]
            st.success(f"Witaj, {username}! Zostałeś zalogowany.")
            st.experimental_rerun()
        else:
            st.error("Nieprawidłowa nazwa użytkownika lub hasło.")

    if st.button("Dostęp Demo"):
        user = authenticate("demo", "demo")
        st.session_state.logged_in = True
        st.session_state.username = user["username"]
        st.session_state.role = user["role"]
        st.experimental_rerun()
else:
    st.success(f"Jesteś zalogowany jako **{st.session_state.username}**.")
    if st.session_state.role == "admin":
        st.subheader("Panel Administratora")
        with st.expander("Zarządzanie użytkownikami"):
            new_username = st.text_input("Nowa nazwa użytkownika")
            new_password = st.text_input("Nowe hasło", type="password")
            new_role = st.selectbox("Rola", ["user", "admin"])
            if st.button("Dodaj użytkownika"):
                df = load_users()
                if new_username in df["username"].values:
                    st.warning("Ta nazwa użytkownika już istnieje.")
                else:
                    new_user = pd.DataFrame([{"username": new_username, "password": new_password, "role": new_role}])
                    df = pd.concat([df, new_user], ignore_index=True)
                    df.to_csv(USERS_FILE, index=False)
                    st.success(f"Dodano nowego użytkownika: **{new_username}**")
                    st.experimental_rerun()
        
    st.markdown("### Przejdź do aplikacji")
    if st.button("Otwórz Dziennik Kalorii"):
        st.switch_page("pages/dziennik_kalorii.py")

    if st.button("Wyloguj"):
        st.session_state.logged_in = False
        st.session_state.username = None
        st.session_state.role = None
        st.experimental_rerun()
