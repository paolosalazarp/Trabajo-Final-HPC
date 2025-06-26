import pandas as pd
import numpy as np
import requests as rq
from bs4 import BeautifulSoup as bs
import re
import os
from multiprocessing import Pool, cpu_count
from concurrent.futures import ProcessPoolExecutor, as_completed
from tqdm import tqdm
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import time
import psutil

# Función auxiliar para obtener datos de un jugador individual
def obtener_datos_jugador_individual(jugador_url):
    """
    Función auxiliar para obtener datos de un jugador individual.
    Esta función será ejecutada en paralelo.
    """
    try:
        # Configurar opciones de Chrome para el proceso individual
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument("--disable-extensions")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        
        driver = webdriver.Chrome(options=options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        # Navegar a la página del jugador
        driver.get(jugador_url)
        time.sleep(2)  # Esperar a que cargue
        
        # Parsear con BeautifulSoup
        soup = bs(driver.page_source, 'html.parser')
        
        # Aquí debes agregar tu lógica específica para extraer los datos del jugador
        # Por ejemplo:
        datos_jugador = {
            'url': jugador_url,
            'nombre': '',
            'equipo': '',
            'valor': '',
            # Agrega más campos según lo que necesites extraer
        }
        
        # Ejemplo de extracción básica (ajusta según la estructura real de la página)
        try:
            # Extraer nombre del jugador
            nombre_element = soup.find('h1')
            if nombre_element:
                datos_jugador['nombre'] = nombre_element.get_text(strip=True)
                
            # Agregar más extracciones según tus necesidades
            # datos_jugador['equipo'] = ...
            # datos_jugador['valor'] = ...
            
        except Exception as e:
            print(f"Error extrayendo datos específicos de {jugador_url}: {e}")
        
        driver.quit()
        return datos_jugador
        
    except Exception as e:
        print(f"Error procesando {jugador_url}: {e}")
        return {'url': jugador_url, 'error': str(e)}

def obtener_todos_datos_jugadores_paralelo(lista_jugadores, max_workers=None):
    """
    Obtiene todos los datos de todos los jugadores usando procesamiento paralelo.
    
    Args:
        lista_jugadores: Lista de URLs de jugadores
        max_workers: Número máximo de workers (por defecto usa todos los CPU cores)
    
    Returns:
        Lista con los datos de todos los jugadores
    """
    
    if max_workers is None:
        max_workers = cpu_count()
    
    print(f"Iniciando scraping paralelo con {max_workers} workers")
    print(f"Total de jugadores a procesar: {len(lista_jugadores)}")
    
    # Iniciar monitoreo de recursos
    inicio_tiempo = time.time()
    inicio_memoria = psutil.virtual_memory().used / (1024 * 1024)  # MB
    
    datos_jugadores = []
    errores = []
    
    # Usar ProcessPoolExecutor para paralelización
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        # Enviar todas las tareas
        futures = {
            executor.submit(obtener_datos_jugador_individual, url): url 
            for url in lista_jugadores
        }
        
        # Procesar resultados conforme van completándose
        for future in tqdm(as_completed(futures), total=len(lista_jugadores), 
                          desc="Procesando jugadores"):
            url = futures[future]
            try:
                resultado = future.result(timeout=30)  # Timeout de 30 segundos por jugador
                
                if 'error' in resultado:
                    errores.append(resultado)
                else:
                    datos_jugadores.append(resultado)
                    
            except Exception as e:
                error_info = {'url': url, 'error': str(e)}
                errores.append(error_info)
                print(f"Error procesando {url}: {e}")
    
    # Calcular métricas finales
    tiempo_total = time.time() - inicio_tiempo
    memoria_final = psutil.virtual_memory().used / (1024 * 1024)  # MB
    memoria_usada = memoria_final - inicio_memoria
    
    print("\n" + "="*60)
    print("RESUMEN DE SCRAPING PARALELO")
    print("="*60)
    print(f"Total de jugadores procesados: {len(datos_jugadores)}")
    print(f"Total de errores: {len(errores)}")
    print(f"Tiempo total: {tiempo_total:.2f} segundos")
    print(f"Velocidad promedio: {len(lista_jugadores)/tiempo_total:.2f} jugadores/segundo")
    print(f"Memoria adicional utilizada: {memoria_usada:.2f} MB")
    print(f"Workers utilizados: {max_workers}")
    print("="*60)
    
    if errores:
        print(f"\nPrimeros 5 errores:")
        for error in errores[:5]:
            print(f"  - {error['url']}: {error['error']}")
    
    return datos_jugadores, errores

# Función optimizada con diferentes niveles de paralelización
def obtener_todos_datos_jugadores_adaptativo(lista_jugadores, modo='auto'):
    """
    Función adaptativa que ajusta el nivel de paralelización según el sistema.
    
    Args:
        lista_jugadores: Lista de URLs de jugadores
        modo: 'conservador', 'balanceado', 'agresivo', 'auto'
    
    Returns:
        Lista con los datos de todos los jugadores
    """
    
    num_cpu = cpu_count()
    memoria_total = psutil.virtual_memory().total / (1024**3)  # GB
    
    if modo == 'conservador':
        workers = max(1, num_cpu // 4)
    elif modo == 'balanceado':
        workers = max(1, num_cpu // 2)
    elif modo == 'agresivo':
        workers = num_cpu
    else:  # auto
        # Decidir automáticamente basado en recursos disponibles
        if memoria_total >= 16:  # 16GB+ RAM
            workers = num_cpu
        elif memoria_total >= 8:   # 8-16GB RAM
            workers = max(1, num_cpu // 2)
        else:  # <8GB RAM
            workers = max(1, num_cpu // 4)
    
    print(f"Modo {modo}: Usando {workers} workers de {num_cpu} CPUs disponibles")
    print(f"Memoria total del sistema: {memoria_total:.1f} GB")
    
    return obtener_todos_datos_jugadores_paralelo(lista_jugadores, workers)

# Función para procesar en lotes (útil para listas muy grandes)
def obtener_todos_datos_jugadores_por_lotes(lista_jugadores, tamaño_lote=100, 
                                           max_workers=None):
    """
    Procesa jugadores en lotes para evitar sobrecargar el sistema.
    
    Args:
        lista_jugadores: Lista de URLs de jugadores
        tamaño_lote: Número de jugadores por lote
        max_workers: Número máximo de workers por lote
    
    Returns:
        Lista con los datos de todos los jugadores
    """
    
    if max_workers is None:
        max_workers = cpu_count()
    
    todos_los_datos = []
    todos_los_errores = []
    
    # Dividir en lotes
    num_lotes = (len(lista_jugadores) + tamaño_lote - 1) // tamaño_lote
    
    for i in range(0, len(lista_jugadores), tamaño_lote):
        lote = lista_jugadores[i:i+tamaño_lote]
        num_lote = i // tamaño_lote + 1
        
        print(f"\nProcesando lote {num_lote}/{num_lotes} ({len(lote)} jugadores)")
        
        datos_lote, errores_lote = obtener_todos_datos_jugadores_paralelo(
            lote, max_workers
        )
        
        todos_los_datos.extend(datos_lote)
        todos_los_errores.extend(errores_lote)
        
        # Pausa pequeña entre lotes para no sobrecargar el servidor
        if i + tamaño_lote < len(lista_jugadores):
            print(f"Pausa de 5 segundos antes del siguiente lote...")
            time.sleep(5)
    
    print(f"\n¡Procesamiento completo! Total: {len(todos_los_datos)} jugadores")
    return todos_los_datos, todos_los_errores