# ⚽ Trabajo Final HPC — Predicción de Valor de Mercado de Jugadores de Fútbol

Proyecto final del curso de **High Performance Computing (HPC)** que combina técnicas de **procesamiento paralelo**, **Cloud Computing**, **web scraping** y **machine learning** para predecir el valor de mercado de jugadores de fútbol a partir de datos extraídos de [SofaScore](https://www.sofascore.com/).

---

## 📋 Tabla de Contenidos

- [Descripción del Proyecto](#descripción-del-proyecto)
- [Arquitectura](#arquitectura)
- [Tecnologías](#tecnologías)
- [Estructura del Repositorio](#estructura-del-repositorio)
- [Requisitos Previos](#requisitos-previos)
- [Instalación y Uso](#instalación-y-uso)
  - [1. Web Scraping Paralelo con Docker](#1-web-scraping-paralelo-con-docker)
  - [2. Entrenamiento del Modelo](#2-entrenamiento-del-modelo)
  - [3. Aplicación Web (Streamlit)](#3-aplicación-web-streamlit)
- [Datos](#datos)
- [Documentos](#documentos)

---

## 📌 Descripción del Proyecto

El objetivo del proyecto es predecir el **valor de mercado** de un jugador de fútbol usando sus estadísticas (ataque, técnica, velocidad, defensa, creatividad, partidos jugados, valoración media y liga). El flujo completo es:

1. **Scraping paralelo**: extracción masiva de datos de jugadores desde SofaScore usando múltiples contenedores Docker.
2. **Entrenamiento**: construcción y optimización de un modelo **Random Forest** con los datos recolectados.
3. **Despliegue**: aplicación web interactiva en **Streamlit** que permite explorar un ranking de jugadores y realizar predicciones individuales.

---

## 🏗️ Arquitectura

```
┌─────────────────────────────────────────────────────────────┐
│                     Docker Compose                          │
│                                                             │
│  ┌─────────────┐      ┌──────────────────────────────┐     │
│  │  Coordinator│─────▶│          Redis Queue         │     │
│  │  (carga URLs│      └──────────┬───────────────────┘     │
│  │   en cola)  │                 │                          │
│  └─────────────┘        ┌────────▼────────┐                │
│                         │  Worker 1–4     │                │
│  ┌──────────────┐       │ (Selenium +     │                │
│  │   Collector  │◀──────│  BeautifulSoup) │                │
│  │ (guarda CSV) │       └─────────────────┘                │
│  └──────────────┘                                          │
└─────────────────────────────────────────────────────────────┘
          │
          ▼
   jugadores_datos_completos.csv
          │
          ▼
   training.ipynb  →  best_random_forest_model.pkl + scaler.pkl
          │
          ▼
        app.py  (Streamlit)
```

El sistema de scraping sigue un patrón **coordinador–worker**:
- El **coordinador** lee las URLs de los jugadores y las encola en Redis.
- Los **workers** (4 contenedores) consumen la cola en paralelo, cada uno con Chrome headless + Selenium.
- El **collector** recupera los resultados de Redis y genera el CSV final.

---

## 🛠️ Tecnologías

| Categoría | Herramientas |
|-----------|-------------|
| Scraping | Selenium, BeautifulSoup4, webdriver-manager |
| Paralelismo | Docker, Docker Compose, Redis |
| Machine Learning | scikit-learn (Random Forest), joblib |
| Datos | Pandas, NumPy |
| Aplicación Web | Streamlit |
| Monitoreo | psutil |
| Lenguaje | Python 3.11 |

---

## 📁 Estructura del Repositorio

```
Trabajo-Final-HPC/
├── app.py                          # Aplicación web Streamlit
├── requirements.txt                # Dependencias para la app Streamlit
├── best_random_forest_model.pkl    # Modelo entrenado (Random Forest)
├── scaler.pkl                      # Scaler para normalización de features
├── training.ipynb                  # Notebook de entrenamiento del modelo
├── scrapeo.ipynb                   # Notebook de scraping secuencial
├── scrapeo_paralelo.ipynb          # Notebook de scraping paralelo
├── jugadores_datos_completos.csv   # Dataset completo de jugadores
├── jugadores_datos.csv             # Dataset parcial
├── jugadores_sofascore.csv         # URLs de jugadores en SofaScore
├── equipos_sofascore.csv           # URLs de equipos en SofaScore
├── datos_finales.csv               # Datos procesados finales
├── primeros.csv                    # Subconjunto inicial de datos
├── Contenedores/                   # Sistema de scraping paralelo con Docker
│   ├── Dockerfile                  # Imagen con Chrome + Python
│   ├── docker-compose.yml          # Orquestación: Redis + coordinator + workers + collector
│   ├── scraper.py                  # Coordinador y workers de scraping
│   ├── collect_results.py          # Recolector de resultados desde Redis
│   ├── jugadores_sofascore.csv     # URLs de entrada para el scraper
│   ├── quick_start.bat             # Script de inicio rápido (Windows)
│   ├── run.bat                     # Script de ejecución (Windows)
│   ├── stop.bat                    # Script de detención (Windows)
│   ├── logs.bat                    # Script para ver logs (Windows)
│   ├── monitor.bat                 # Script de monitoreo (Windows)
│   ├── status.bat                  # Script de estado (Windows)
│   └── check_setup.bat             # Script de verificación (Windows)
└── Documentos/
    ├── Informe Final.pdf           # Informe del proyecto
    └── CLOUD PPT FINAL .pdf        # Presentación del proyecto
```

---

## ✅ Requisitos Previos

- **Python 3.11+**
- **Docker** y **Docker Compose** (para el scraping paralelo)
- **Git**

---

## 🚀 Instalación y Uso

### 1. Web Scraping Paralelo con Docker

El sistema de scraping se encuentra en la carpeta `Contenedores/`. Levanta un coordinador, 4 workers y un recolector de resultados, todos comunicados a través de Redis.

```bash
cd Contenedores/

# Construir y levantar todos los servicios
docker-compose up --build

# Ver los logs en tiempo real
docker-compose logs -f

# Detener todos los servicios
docker-compose down
```

**Scripts de Windows disponibles:**

```bat
quick_start.bat   # Inicia todo el sistema
logs.bat          # Muestra los logs de todos los contenedores
monitor.bat       # Monitorea el estado del scraping
status.bat        # Muestra el estado de los servicios
stop.bat          # Detiene y elimina los contenedores
```

Los resultados se guardan automáticamente en `Contenedores/results/jugadores_datos_completos.csv`.

---

### 2. Entrenamiento del Modelo

Abre el notebook `training.ipynb` en Jupyter y ejecútalo por completo. El notebook:

1. Carga y limpia los datos desde `jugadores_datos_completos.csv`.
2. Realiza ingeniería de características (codificación de liga, etc.).
3. Entrena y optimiza un modelo **Random Forest** con búsqueda de hiperparámetros.
4. Guarda el modelo (`best_random_forest_model.pkl`) y el scaler (`scaler.pkl`).

```bash
pip install -r requirements.txt
jupyter notebook training.ipynb
```

---

### 3. Aplicación Web (Streamlit)

La aplicación permite:
- Ver el **Top 10 de jugadores** por valor de mercado, con filtros por liga, nacionalidad y edad.
- **Predecir el valor de mercado** de un jugador ingresando sus estadísticas manualmente.

```bash
# Instalar dependencias
pip install -r requirements.txt

# Ejecutar la aplicación
streamlit run app.py
```

La aplicación estará disponible en `http://localhost:8501`.

---

## 📊 Datos

Los datos fueron extraídos de [SofaScore](https://www.sofascore.com/) e incluyen las siguientes características por jugador:

| Campo | Descripción |
|-------|-------------|
| `Nombre` | Nombre del jugador |
| `Edad` | Edad del jugador |
| `Liga` | Liga en la que compite |
| `Nacionalidad` | País de origen |
| `ataque` | Puntuación de ataque (0–100) |
| `tecnica` | Puntuación de técnica (0–100) |
| `velocidad` | Puntuación de velocidad (0–100) |
| `defensa` | Puntuación de defensa (0–100) |
| `creatividad` | Puntuación de creatividad (0–100) |
| `partidos` | Número de partidos jugados |
| `valoracion_media` | Valoración media en la plataforma |
| `valor_mercado` | Valor de mercado en euros (variable objetivo) |

---

## 📄 Documentos

En la carpeta `Documentos/` se encuentran el informe técnico y la presentación completa del proyecto:

- `Informe Final.pdf` — Descripción detallada de la metodología, experimentos y resultados.
- `CLOUD PPT FINAL .pdf` — Presentación ejecutiva del proyecto.
