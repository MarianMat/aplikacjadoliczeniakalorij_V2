import streamlit as st
from datetime import datetime, timedelta
from utils import init_db, add_user, verify_user, update_first_use, get_first_use

st.set_page_config(page_title="Aplikacja Liczenia Kalorii", page_icon="🍎")

init_db()

user_avatars = {
    "Chmarynka": "🌥️",
    "Demo": "🆓",
}

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_name" not in st.session_state:
    st.session_state.user_name = ""

def register():
    st.subheader("Rejestracja")
    username = st.text_input("Nazwa użytkownika (login)", key="reg_username")
    password = st.text_input("Hasło", type="password", key="reg_password")
    email = st.text_input("Email (opcjonalnie)", key="reg_email")
    if st.button("Zarejestruj"):
        if not username or not password:
            st.error("Podaj nazwę użytkownika i hasło.")
            return
        if add_user(username.strip(), password.strip(), email.strip()):
            st.success("Zarejestrowano pomyślnie! Możesz się teraz zalogować.")
        else:
            st.error("Użytkownik o tej nazwie już istnieje.")

def login():
    st.subheader("Logowanie")
    username = st.text_input("Nazwa użytkownika", key="login_username")
    password = st.text_input("Hasło", type="password", key="login_password")
    if st.button("Zaloguj"):
        if verify_user(username.strip(), password.strip()):
            st.session_state.logged_in = True
            st.session_state.user_name = username.strip()
            update_first_use(st.session_state.user_name)
            st.experimental_rerun()
        else:
            st.error("Nieprawidłowy login lub hasło.")

if not st.session_state.logged_in:
    st.title("Witamy w aplikacji liczenia kalorii 🍏")
    register()
    st.markdown("---")
    login()
    st.stop()

first_use_str = get_first_use(st.session_state.user_name)
if first_use_str:
    first_use = datetime.fromisoformat(first_use_str)
    if datetime.now() - first_use > timedelta(days=1):
        st.warning(
            f"Twoja wersja demo konta '{st.session_state.user_name}' zakończyła się. "
            "Skontaktuj się z autorem aplikacji, aby uzyskać pełny dostęp."
        )
        st.stop()

avatar = user_avatars.get(st.session_state.user_name, "👤")
st.title(f"Witaj, {avatar} {st.session_state.user_name}!")
st.write("Tu możesz korzystać z aplikacji liczenia kalorii i innych funkcji.")

# --- Tutaj możesz dopisać dalszą funkcjonalność aplikacji ---
