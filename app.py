import streamlit as st
import pandas as pd
from datetime import datetime, date
import os

# Ścieżka do pliku z danymi
DATA_PATH = "data/posilki.csv"

# Inicjalizacja danych
def load_data():
    if not os.path.exists(DATA_PATH):
        df = pd.DataFrame(columns=["data", "czas", "produkt", "waga", "kalorie", "typ"])
        df.to_csv(DATA_PATH, index=False)
    return pd.read_csv(DATA_PATH)

def save_data(df):
    df.to_csv(DATA_PATH, index=False)

# Interfejs
st.set_page_config("Dziennik Kalorii", layout="centered", page_icon="🍽️")
st.title("🍽️ Dziennik posiłków")

df = load_data()
today = date.today().strftime("%Y-%m-%d")
df_today = df[df["data"] == today]

cel_kalorii = 2200
spozyto = df_today["kalorie"].sum()

# Nagłówek
st.markdown(f"""
### 📅 Dziś: {today}
🎯 Cel: **{cel_kalorii} kcal**  
🔥 Spożyto: **{spozyto} kcal**
""")

with st.expander("➕ Dodaj posiłek"):
    produkt = st.text_input("Nazwa produktu")
    waga = st.number_input("Waga (g)", min_value=0)
    kalorie = st.number_input("Kalorie", min_value=0)
    typ = st.selectbox("Typ posiłku", ["Śniadanie", "Obiad", "Kolacja", "Przekąska", "Inne"])
    czas = st.time_input("Godzina spożycia", value=datetime.now().time())

    if st.button("💾 Zapisz"):
        now = datetime.now()
        new_row = {
            "data": today,
            "czas": czas.strftime("%H:%M"),
            "produkt": produkt,
            "waga": waga,
            "kalorie": kalorie,
            "typ": typ
        }
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        save_data(df)
        st.success("Dodan
