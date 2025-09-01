import streamlit as st
import pandas as pd
from datetime import datetime, date
import os
import requests
import base64

# Sprawdzenie, czy użytkownik jest zalogowany
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("Proszę zalogować się, aby uzyskać dostęp do aplikacji.")
    st.stop()

# Ścieżka do pliku z danymi (dla danego użytkownika)
DATA_PATH = f"data/posilki_{st.session_state.username}.csv"

# Inicjalizacja danych
def load_data():
    if not os.path.exists("data"):
        os.makedirs("data")
    if not os.path.exists(DATA_PATH):
        df = pd.DataFrame(columns=["data", "czas", "produkt", "waga", "kalorie", "typ", "białko", "tłuszcz", "węglowodany"])
        df.to_csv(DATA_PATH, index=False)
    return pd.read_csv(DATA_PATH)

def save_data(df):
    df.to_csv(DATA_PATH, index=False)

# Funkcja do wysyłania zdjęcia do API
def analyze_image_with_api(image_bytes):
    # Klucz API z Streamlit Secrets
    API_KEY = st.secrets["api_keys"]["image_recognition_key"]
    # Poniższy kod jest tylko szkieletem.
    API_URL = "https://example.com/api/v1/analyze"
    
    try:
        encoded_string = base64.b64encode(image_bytes).decode('utf-8')
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {API_KEY}"}
        payload = {"image": encoded_string}
        
        response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        if result and "labels" in result and result["labels"]:
            return result["labels"][0]["name"]
    except (requests.exceptions.RequestException, KeyError) as e:
        st.error(f"Błąd API: {e}")
    return None

# Funkcja do pobierania danych z API na podstawie kodu kreskowego
def get_product_by_barcode(barcode):
    # Klucze API z Streamlit Secrets
    APP_ID = st.secrets["api_keys"]["nutritionix_app_id"]
    APP_KEY = st.secrets["api_keys"]["nutritionix_app_key"]
    
    URL = "https://api.nutritionix.com/v1_1/item"
    headers = {"Content-Type": "application/json"}
    payload = {
        "upc": barcode,
        "appId": APP_ID,
        "appKey": APP_KEY
    }

    try:
        response = requests.post(URL, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if "foods" in data and data["foods"]:
            food = data["foods"][0]
            product_info = {
                "produkt": food.get("food_name", "Nieznany produkt"),
                "kalorie": food.get("nf_calories"),
                "białko": food.get("nf_protein"),
                "tłuszcz": food.get("nf_total_fat"),
                "węglowodany": food.get("nf_total_carbohydrate")
            }
            return product_info
    except (requests.exceptions.RequestException, KeyError) as e:
        st.error(f"Błąd API: {e}")
    return None

# Funkcja do wyszukiwania produktu w bazie online (np. Nutritionix)
def search_product_online(query):
    # Klucze API z Streamlit Secrets
    APP_ID = st.secrets["api_keys"]["nutritionix_app_id"]
    APP_KEY = st.secrets["api_keys"]["nutritionix_app_key"]
    
    URL = "https://api.nutritionix.com/v1_1/search/items"
    headers = {"Content-Type": "application/json"}
    payload = {
        "appId": APP_ID,
        "appKey": APP_KEY,
        "query": query
    }

    try:
        response = requests.post(URL, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if "hits" in data and data["hits"]:
            results = []
            for item in data["hits"]:
                fields = item.get("fields", {})
                results.append({
                    "nazwa": fields.get("item_name"),
                    "kalorie": fields.get("nf_calories"),
                    "białko": fields.get("nf_protein"),
                    "tłuszcz": fields.get("nf_total_fat"),
                    "węglowodany": fields.get("nf_total_carbohydrate")
                })
            return results
    except (requests.exceptions.RequestException, KeyError) as e:
        st.error(f"Błąd API: {e}")
    return None

# Interfejs
st.set_page_config("Dziennik Kalorii", layout="centered", page_icon="🍽️")
st.title("🍽️ Dziennik posiłków")
st.markdown(f"Zalogowany jako **{st.session_state.username}**")

df = load_data()
today = date.today().strftime("%Y-%m-%d")
df_today = df[df["data"] == today]

cel_kalorii = 2200
spozyto = df_today["kalorie"].sum()

# Nagłówek i pasek postępu
st.markdown(f"### 📅 Dziś: {today}")
st.progress(spozyto / cel_kalorii if cel_kalorii > 0 else 0)
st.markdown(f"""
🎯 Cel: **{cel_kalorii} kcal**
🔥 Spożyto: **{spozyto} kcal**
""")

with st.expander("➕ Dodaj posiłek"):
    st.subheader("Jak chcesz dodać posiłek?")
    
    opcja = st.radio("Wybierz opcję dodawania:", ["Ręcznie", "Ze zdjęcia", "Z bazy danych online", "Ze skanu kodu kreskowego"])

    if opcja == "Ręcznie":
        produkt = st.text_input("Nazwa produktu")
        waga = st.number_input("Waga (g)", min_value=0)
        kalorie = st.number_input("Kalorie", min_value=0)
        białko = st.number_input("Białko (g)", min_value=0.0)
        tłuszcz = st.number_input("Tłuszcz (g)", min_value=0.0)
        węglowodany = st.number_input("Węglowodany (g)", min_value=0.0)
        typ = st.selectbox("Typ posiłku", ["Śniadanie", "Obiad", "Kolacja", "Przekąska", "Inne"])
        czas = st.time_input("Godzina spożycia", value=datetime.now().time())

        if st.button("💾 Zapisz posiłek"):
            if not produkt or not waga or not kalorie:
                st.error("Wypełnij wszystkie wymagane pola.")
            else:
                new_row = {
                    "data": today,
                    "czas": czas.strftime("%H:%M"),
                    "produkt": produkt,
                    "waga": waga,
                    "kalorie": kalorie,
                    "typ": typ,
                    "białko": białko,
                    "tłuszcz": tłuszcz,
                    "węglowodany": węglowodany
                }
                df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                save_data(df)
                st.success("Dodano posiłek!")
                st.experimental_rerun()

    elif opcja == "Ze zdjęcia":
        uploaded_file = st.file_uploader("Prześlij zdjęcie posiłku", type=["jpg", "jpeg", "png"])
        if uploaded_file is not None:
            st.image(uploaded_file, caption='Twoje zdjęcie', use_column_width=True)
            with st.spinner("Analizuję zdjęcie..."):
                file_bytes = uploaded_file.getvalue()
                detected_product = analyze_image_with_api(file_bytes)
            
            if detected_product:
                st.success(f"Wykryto: **{detected_product}**")
                final_product_name = st.text_input("Popraw nazwę produktu (jeśli jest nieprawidłowa)", value=detected_product)
                
                waga = st.number_input("Waga (g)", min_value=0)
                kalorie = st.number_input("Kalorie", min_value=0)
                białko = st.number_input("Białko (g)", min_value=0.0)
                tłuszcz = st.number_input("Tłuszcz (g)", min_value=0.0)
                węglowodany = st.number_input("Węglowodany (g)", min_value=0.0)
                typ = st.selectbox("Typ posiłku", ["Śniadanie", "Obiad", "Kolacja", "Przekąska", "Inne"])
                czas = st.time_input("Godzina spożycia", value=datetime.now().time())

                if st.button("💾 Zapisz posiłek z zdjęcia"):
                    if not final_product_name or not waga or not kalorie:
                        st.error("Wypełnij pola, aby zapisać posiłek.")
                    else:
                        new_row = {
                            "data": today,
                            "czas": czas.strftime("%H:%M"),
                            "produkt": final_product_name,
                            "waga": waga,
                            "kalorie": kalorie,
                            "typ": typ,
                            "białko": białko,
                            "tłuszcz": tłuszcz,
                            "węglowodany": węglowodany
                        }
                        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                        save_data(df)
                        st.success("Dodano posiłek!")
                        st.experimental_rerun()
            else:
                st.warning("Nie udało się rozpoznać produktu na zdjęciu. Spróbuj dodać go ręcznie.")
    
    elif opcja == "Z bazy danych online":
        query = st.text_input("Wpisz nazwę produktu (np. 'jabłko', 'pierś z kurczaka')")
        if st.button("🔎 Wyszukaj"):
            with st.spinner("Wyszukuję..."):
                results = search_product_online(query)
            if results:
                st.success(f"Znaleziono {len(results)} wyników.")
                
                options = [f"{item['nazwa']} - {item['kalorie']} kcal" for item in results if item.get('kalorie') is not None]
                selected_option = st.selectbox("Wybierz produkt:", options)
                
                if selected_option:
                    selected_item = next((item for item in results if f"{item['nazwa']} - {item.get('kalorie')} kcal" == selected_option), None)
                    
                    if selected_item:
                        produkt = selected_item.get('nazwa', '')
                        st.markdown(f"**Wybrano:** {produkt}")
                        waga = st.number_input("Waga (g)", min_value=0)
                        kalorie = st.number_input("Kalorie", value=int(selected_item.get('kalorie', 0) or 0), disabled=True)
                        białko = st.number_input("Białko (g)", value=selected_item.get('białko', 0.0), disabled=True)
                        tłuszcz = st.number_input("Tłuszcz (g)", value=selected_item.get('tłuszcz', 0.0), disabled=True)
                        węglowodany = st.number_input("Węglowodany (g)", value=selected_item.get('węglowodany', 0.0), disabled=True)
                        typ = st.selectbox("Typ posiłku", ["Śniadanie", "Obiad", "Kolacja", "Przekąska", "Inne"])
                        czas = st.time_input("Godzina spożycia", value=datetime.now().time())

                        if st.button("💾 Zapisz wybrany produkt"):
                            if not waga:
                                st.error("Podaj wagę, aby zapisać posiłek.")
                            else:
                                new_row = {
                                    "data": today,
                                    "czas": czas.strftime("%H:%M"),
                                    "produkt": produkt,
                                    "waga": waga,
                                    "kalorie": kalorie,
                                    "typ": typ,
                                    "białko": białko,
                                    "tłuszcz": tłuszcz,
                                    "węglowodany": węglowodany
                                }
                                df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                                save_data(df)
                                st.success("Dodano posiłek!")
                                st.experimental_rerun()
            else:
                st.warning("Nie znaleziono produktów. Spróbuj zmienić zapytanie.")
    
    elif opcja == "Ze skanu kodu kreskowego":
        barcode = st.text_input("Wpisz kod kreskowy (EAN)")
        if st.button("🔎 Skanuj"):
            if not barcode:
                st.error("Wpisz kod kreskowy, aby wyszukać produkt.")
            else:
                with st.spinner(f"Skanuję kod: {barcode}..."):
                    product_info = get_product_by_barcode(barcode)
                
                if product_info and product_info.get('kalorie') is not None:
                    st.success("Znaleziono produkt!")
                    st.markdown(f"**Produkt:** {product_info['produkt']}")
                    
                    waga = st.number_input("Waga (g)", min_value=0)
                    kalorie = st.number_input("Kalorie", value=int(product_info.get('kalorie', 0) or 0), disabled=True)
                    białko = st.number_input("Białko (g)", value=product_info.get('białko', 0.0), disabled=True)
                    tłuszcz = st.number_input("Tłuszcz (g)", value=product_info.get('tłuszcz', 0.0), disabled=True)
                    węglowodany = st.number_input("Węglowodany (g)", value=product_info.get('węglowodany', 0.0), disabled=True)
                    typ = st.selectbox("Typ posiłku", ["Śniadanie", "Obiad", "Kolacja", "Przekąska", "Inne"])
                    czas = st.time_input("Godzina spożycia", value=datetime.now().time())

                    if st.button("💾 Zapisz zeskanowany produkt"):
                        if not waga:
                            st.error("Podaj wagę, aby zapisać posiłek.")
                        else:
                            new_row = {
                                "data": today,
                                "czas": czas.strftime("%H:%M"),
                                "produkt": product_info['produkt'],
                                "waga": waga,
                                "kalorie": kalorie,
                                "typ": typ,
                                "białko": białko,
                                "tłuszcz": tłuszcz,
                                "węglowodany": węglowodany
                            }
                            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                            save_data(df)
                            st.success("Dodano posiłek!")
                            st.experimental_rerun()
                else:
                    st.warning("Nie znaleziono produktu o podanym kodzie kreskowym.")

# Lista posiłków
st.subheader("🍴 Posiłki dzisiaj")
if df_today.empty:
    st.info("Brak posiłków na dziś.")
else:
    for _, row in df_today.iterrows():
        st.markdown(f"• 🕒 {row['czas']} – **{row['produkt']}** ({int(row['waga'])}g) – **{int(row['kalorie'])} kcal** | Białko: {row['białko']:.1f}g, Tłuszcz: {row['tłuszcz']:.1f}g, Węglowodany: {row['węglowodany']:.1f}g ({row['typ']})")
    for _, row in df_today.iterrows():
        st.markdown(f"• 🕒 {row['czas']} – **{row['produkt']}** ({int(row['waga'])}g) – **{int(row['kalorie'])} kcal** | Białko: {row['białko']:.1f}g, Tłuszcz: {row['tłuszcz']:.1f}g, Węglowodany: {row['węglowodany']:.1f}g ({row['typ']})")
