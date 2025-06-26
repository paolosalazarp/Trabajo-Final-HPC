import streamlit as st
import pandas as pd
import numpy as np
import joblib

# ----------------- CONFIGURACIÓN INICIAL -----------------
st.set_page_config(page_title="Predicción Valor de Jugadores", layout="wide")

# Cargar el modelo y el scaler
@st.cache_resource
def load_model_scaler():
    model = joblib.load("best_random_forest_model.pkl")
    scaler = joblib.load("scaler.pkl")
    return model, scaler

# Cargar el dataset
@st.cache_data
def load_data():
    return pd.read_csv("jugadores_datos_completos.csv")

# Cargar recursos
data = load_data()
model, scaler = load_model_scaler()

# Definir las features usadas por el modelo
input_features = [
    "ataque", "tecnica", "velocidad", "defensa",
    "creatividad", "partidos", "valoracion_media", "liga_num"
]

# ----------------- TÍTULO PRINCIPAL -----------------
st.title("🌍⚽ Predicción de Valor de Mercado de Jugadores")

# ----------------- SECCIÓN DE FILTROS -----------------
st.sidebar.header("🎯 Filtros para el ranking")

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

# ----------------- TOP 10 JUGADORES -----------------
st.subheader("💸 Top 10 jugadores por valor de mercado")
top_players = filtered_data.sort_values(by="valor_mercado", ascending=False).head(10)
st.dataframe(top_players[["Nombre", "Edad", "Liga", "Nacionalidad", "valor_mercado"]].reset_index(drop=True))

# ----------------- FORMULARIO DE PREDICCIÓN -----------------
st.subheader("🧠 Ingreso de datos para predecir valor")

form = st.form("predict_form")
player_input = []

for feature in input_features:
    mean_val = float(data[feature].dropna().mean())
    val = form.number_input(f"{feature}", value=mean_val)
    player_input.append(val)

submit = form.form_submit_button("Predecir valor de mercado")

if submit:
    try:
        player_array = np.array(player_input).reshape(1, -1)
        scaled_input = scaler.transform(player_array)
        prediction = model.predict(scaled_input)[0]
        st.success(f"✅ Valor de mercado estimado: €{prediction:,.2f}")
    except Exception as e:
        st.error(f"❌ Error al predecir: {e}")
