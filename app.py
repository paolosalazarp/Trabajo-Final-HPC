import streamlit as st
import pandas as pd
import numpy as np
import joblib

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

# Inicialización
st.title("⚽ Predicción del Valor de Mercado de Jugadores")

# Cargar datos y modelo
data = load_data()
model, scaler = load_model_scaler()

# Separar características de entrada
X = data.drop(columns=["valor_mercado"])
y = data["valor_mercado"]

# Columnas categóricas para filtro
st.sidebar.header("🎯 Filtros de jugadores")
selected_league = st.sidebar.selectbox("Liga", ["Todas"] + sorted(data["Liga"].dropna().unique()))
selected_nationality = st.sidebar.selectbox("Nacionalidad", ["Todas"] + sorted(data["Nacionalidad"].dropna().unique()))
max_age = int(data["Edad"].max())
selected_age = st.sidebar.slider("Edad máxima", 16, max_age, max_age)

# Filtrar tabla
filtered_data = data.copy()
if selected_league != "Todas":
    filtered_data = filtered_data[filtered_data["Liga"] == selected_league]
if selected_nationality != "Todas":
    filtered_data = filtered_data[filtered_data["Nacionalidad"] == selected_nationality]
filtered_data = filtered_data[filtered_data["Edad"] <= selected_age]

# Mostrar top 10 por valor de mercado
st.subheader("💸 Top 10 jugadores por valor de mercado")
top_players = filtered_data.sort_values(by="valor_mercado", ascending=False).head(10)
st.dataframe(top_players[["Nombre", "Edad", "Liga", "Nacionalidad", "valor_mercado"]].reset_index(drop=True))

# Entradas para predicción
st.subheader("📈 Ingresar datos de un jugador para estimar su valor de mercado")

# Solo usar columnas numéricas del conjunto de entrada X
input_features = X.select_dtypes(include=["number"]).columns.tolist()
player_input = []

for feature in input_features:
    default_val = float(X[feature].mean())
    val = st.number_input(f"{feature}", value=default_val)
    player_input.append(val)

# Hacer predicción
if st.button("🔍 Predecir valor de mercado"):
    try:
        player_array = np.array(player_input).reshape(1, -1)
        scaled_input = scaler.transform(player_array)
        prediction = model.predict(scaled_input)[0]
        st.success(f"✅ Valor de mercado estimado: €{prediction:,.2f}")
    except Exception as e:
        st.error(f"❌ Error al predecir: {e}")

