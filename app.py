import streamlit as st
import pandas as pd
import joblib
import numpy as np

# Cargar datos y modelo
@st.cache_data
def load_data():
    data = pd.read_csv("jugadores_datos_completos.csv")
    return data

@st.cache_resource
def load_model():
    model = joblib.load("best_random_forest_model.pkl")
    scaler = joblib.load("scaler.pkl")
    return model, scaler

data = load_data()
model, scaler = load_model()

# Título
st.title("⚽ Predicción de Valor de Mercado de Jugadores")

# Sección de Predicción
st.sidebar.header("🧠 Ingreso de datos para predicción")
st.sidebar.markdown("Ingresa los datos del jugador para predecir su valor.")

# Obtener columnas numéricas para predicción (debes ajustarlas según las que usó tu modelo)
input_features = [col for col in data.columns if col not in ["Nombre", "Valor", "Liga", "Nacionalidad"]]  # Excluye columnas que no son features
player_input = []

for feature in input_features:
    val = st.sidebar.number_input(f"{feature}", value=float(data[feature].mean()))
    player_input.append(val)

# Botón de predicción
if st.sidebar.button("Predecir valor de mercado"):
    try:
        player_array = np.array(player_input).reshape(1, -1)
        scaled_input = scaler.transform(player_array)
        prediction = model.predict(scaled_input)[0]
        st.sidebar.success(f"💰 Valor estimado: €{prediction:,.2f}")
    except Exception as e:
        st.sidebar.error(f"Error en la predicción: {e}")

# Sección del top jugadores
st.subheader("📊 Top Jugadores por Valor de Mercado")

# Filtros
col1, col2, col3 = st.columns(3)

with col1:
    selected_league = st.selectbox("Filtrar por liga", ["Todas"] + sorted(data["Liga"].unique()))
with col2:
    selected_nationality = st.selectbox("Filtrar por nacionalidad", ["Todas"] + sorted(data["Nacionalidad"].unique()))
with col3:
    max_age = int(data["Edad"].max())
    selected_age = st.slider("Filtrar por edad máxima", 16, max_age, max_age)

filtered_data = data.copy()
if selected_league != "Todas":
    filtered_data = filtered_data[filtered_data["Liga"] == selected_league]
if selected_nationality != "Todas":
    filtered_data = filtered_data[filtered_data["Nacionalidad"] == selected_nationality]
filtered_data = filtered_data[filtered_data["Edad"] <= selected_age]

# Mostrar top 10
top_players = filtered_data.sort_values(by="Valor", ascending=False).head(10)
st.dataframe(top_players[["Nombre", "Edad", "Liga", "Nacionalidad", "Valor"]].reset_index(drop=True))
