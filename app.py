import streamlit as st
import pandas as pd
import numpy as np
import joblib

# ----------------- CONFIGURACIÓN INICIAL -----------------
st.set_page_config(page_title="Predicción Valor de Jugadores", layout="wide")

# ----------------- CARGA DE MODELO Y DATOS -----------------
@st.cache_resource
def load_model_scaler():
    model = joblib.load("best_random_forest_model.pkl")
    scaler = joblib.load("scaler.pkl")
    return model, scaler

@st.cache_data
def load_data():
    df = pd.read_csv("jugadores_datos_completos.csv")
    df = df.loc[:, ~df.columns.str.startswith("Unnamed")]  # Eliminar columnas basura
    return df

model, scaler = load_model_scaler()
data = load_data()

# ----------------- VARIABLES USADAS POR EL MODELO -----------------
input_features = [
    "ataque", "tecnica", "velocidad", "defensa",
    "creatividad", "partidos", "valoracion_media", "liga_num"
]

# ----------------- FILTROS LATERALES -----------------
st.sidebar.header("🎯 Filtros para ranking de jugadores")

selected_league = st.sidebar.selectbox("Liga", ["Todas"] + sorted(data["Liga"].dropna().unique()))
selected_nationality = st.sidebar.selectbox("Nacionalidad", ["Todas"] + sorted(data["Nacionalidad"].dropna().unique()))
max_age = int(data["Edad"].max())
selected_age = st.sidebar.slider("Edad máxima", 16, max_age, max_age)

filtered_data = data.copy()
if selected_league != "Todas":
    filtered_data = filtered_data[filtered_data["Liga"] == selected_league]
if selected_nationality != "Todas":
    filtered_data = filtered_data[filtered_data["Nacionalidad"] == selected_nationality]
filtered_data = filtered_data[filtered_data["Edad"] <= selected_age]

# ----------------- TÍTULO Y TOP JUGADORES -----------------
st.title("🌍⚽ Predicción de Valor de Mercado de Jugadores")

st.subheader("💸 Top 10 jugadores por valor de mercado")
top_players = filtered_data.sort_values(by="valor_mercado", ascending=False).head(10)
st.dataframe(top_players[["Nombre", "Edad", "Liga", "Nacionalidad", "valor_mercado"]].reset_index(drop=True))

# ----------------- FORMULARIO DE PREDICCIÓN -----------------
st.subheader("🧠 Ingreso de datos para predecir valor")

with st.form("prediction_form"):
    player_input = []
    for feature in input_features:
        default = float(data[feature].dropna().mean())
        val = st.number_input(f"{feature}", value=default)
        player_input.append(val)

    submitted = st.form_submit_button("🔍 Predecir valor de mercado")

    if submitted:
        try:
            input_array = np.array(player_input).reshape(1, -1)
            scaled = scaler.transform(input_array)
            prediction = model.predict(scaled)[0]
            st.success(f"✅ Valor de mercado estimado: €{prediction:,.2f}")
        except Exception as e:
            st.error(f"❌ Error durante la predicción: {e}")
