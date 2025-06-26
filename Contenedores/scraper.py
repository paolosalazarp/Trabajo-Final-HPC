import psutil
import time
import pandas as pd
import numpy as np
import requests as rq
from bs4 import BeautifulSoup as bs
import re
import os
import sys
import redis
from multiprocessing import Pool
from tqdm import tqdm
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

class MonitorSimple:
    def __init__(self):
        self.inicio_tiempo = None
        self.inicio_cpu = None
        self.inicio_memoria = None
        self.max_cpu = 0
        self.max_memoria = 0
        self.muestras_cpu = []
        self.muestras_memoria = []
    
    def iniciar(self):
        """Inicia el monitoreo"""
        self.inicio_tiempo = time.time()
        self.inicio_cpu = psutil.cpu_percent()
        self.inicio_memoria = psutil.virtual_memory().percent
        print("Monitoreo de recursos iniciado...")
    
    def actualizar(self):
        """Actualiza las métricas (llamar periódicamente durante el scraping)"""
        cpu_actual = psutil.cpu_percent()
        memoria_actual = psutil.virtual_memory().percent
        
        self.max_cpu = max(self.max_cpu, cpu_actual)
        self.max_memoria = max(self.max_memoria, memoria_actual)
        self.muestras_cpu.append(cpu_actual)
        self.muestras_memoria.append(memoria_actual)
    
    def finalizar(self):
        """Muestra la métrica final"""
        tiempo_total = time.time() - self.inicio_tiempo
        cpu_promedio = sum(self.muestras_cpu) / len(self.muestras_cpu) if self.muestras_cpu else 0
        memoria_promedio = sum(self.muestras_memoria) / len(self.muestras_memoria) if self.muestras_memoria else 0
        
        print("\n" + "="*60)
        print("METRICAS FINALES DE RECURSOS")
        print("="*60)
        print(f"Tiempo total: {tiempo_total:.1f} segundos")
        print(f"CPU - Promedio: {cpu_promedio:.1f}% | Maximo: {self.max_cpu:.1f}%")
        print(f"RAM - Promedio: {memoria_promedio:.1f}% | Maximo: {self.max_memoria:.1f}%")
        print(f"Muestras tomadas: {len(self.muestras_cpu)}")
        print("="*60)

class JobQueue:
    def __init__(self, redis_host='redis', redis_port=6379):
        try:
            self.redis_client = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)
            # Verificar conexión
            self.redis_client.ping()
        except:
            print("No se pudo conectar a Redis, usando modo sin cola")
            self.redis_client = None
        
        self.queue_name = 'player_urls'
        self.results_key = 'scraping_results'
        self.errors_key = 'scraping_errors'
    
    def add_jobs(self, urls):
        """Añade URLs a la cola de trabajos"""
        if not self.redis_client:
            return False
            
        for url in urls:
            self.redis_client.lpush(self.queue_name, url.strip())
        print(f"{len(urls)} URLs añadidas a la cola")
        return True
    
    def get_job(self):
        """Obtiene el siguiente trabajo de la cola"""
        if not self.redis_client:
            return None
        return self.redis_client.rpop(self.queue_name)
    
    def save_result(self, result):
        """Guarda un resultado exitoso"""
        if self.redis_client:
            self.redis_client.lpush(self.results_key, str(result))
    
    def save_error(self, error):
        """Guarda un error"""
        if self.redis_client:
            self.redis_client.lpush(self.errors_key, str(error))
    
    def get_queue_size(self):
        """Obtiene el tamaño de la cola"""
        if not self.redis_client:
            return 0
        return self.redis_client.llen(self.queue_name)

def crear_driver():
    """Crea una instancia del driver de Chrome"""
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument('--window-size=1920,1080')
    
    driver = webdriver.Chrome(options=options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    return driver

def extraer_datos_jugador(jugador_url):
    """Extrae los datos de un jugador individual"""
    driver = None
    try:
        driver = crear_driver()
        driver.get(jugador_url)
        wait = WebDriverWait(driver, 10)
        
        # Diccionario para almacenar datos del jugador
        datos_jugador = {'url': jugador_url}
        
        # 1. Nombre del jugador
        try:
            nombre_element = driver.find_element(By.XPATH, "//h1[contains(@class, 'Text')]")
            datos_jugador['nombre'] = nombre_element.text.strip()
        except:
            datos_jugador['nombre'] = None
        
        # 2. Posición
        try:
            posicion_element = driver.find_element(By.XPATH, "//span[contains(@class, 'Text') and contains(@class, 'fzFbgV')]")
            datos_jugador['posicion'] = posicion_element.text.strip()
        except:
            datos_jugador['posicion'] = None
        
        # 3. Equipo actual
        try:
            equipo_element = driver.find_element(By.XPATH, "//a[contains(@href, '/team/football')]")
            datos_jugador['equipo'] = equipo_element.text.strip().split("\n")[0]
        except:
            datos_jugador['equipo'] = None
        
        # 4. Nacionalidad
        try:
            nacionalidad_element = driver.find_element(By.XPATH, "//img[contains(@alt, 'country flag')]")
            datos_jugador['nacionalidad'] = nacionalidad_element.get_attribute('alt').replace(' country flag', '')
        except:
            datos_jugador['nacionalidad'] = None
        
        # 5. Edad
        try:
            edad_element = driver.find_element(By.XPATH, "//span[contains(text(), 'years old')]")
            datos_jugador['edad'] = edad_element.text.replace(' years old', '').strip()
        except:
            datos_jugador['edad'] = None
        
        # 6. Altura
        try:
            altura_element = driver.find_element(By.XPATH, "//span[contains(text(), 'cm')]")
            datos_jugador['altura'] = altura_element.text.strip()
        except:
            datos_jugador['altura'] = None
        
        # 7. Valor de mercado
        try:
            valor_element = driver.find_element(By.XPATH, "//div[contains(@class, 'Text imGAlA')]")
            datos_jugador['valor_mercado'] = valor_element.text.strip()
        except:
            datos_jugador['valor_mercado'] = None
        
        # 8-12. Estadísticas de habilidades
        try:
            stats_elements = driver.find_elements(By.XPATH, "//span[contains(@class, 'textStyle_table.small c_surface.s1 lh_20px d_block ta_center')]")
            stats_names = ['ataque', 'tecnica', 'velocidad', 'defensa', 'creatividad']
            for i, stat_name in enumerate(stats_names):
                if i < len(stats_elements):
                    datos_jugador[stat_name] = stats_elements[i].text.strip()
                else:
                    datos_jugador[stat_name] = None
        except:
            for stat_name in ['ataque', 'tecnica', 'velocidad', 'defensa', 'creatividad']:
                datos_jugador[stat_name] = None
        
        # 13. Liga actual
        try:
            liga_element = driver.find_element(By.XPATH, "//a[contains(@href, '/tournament/football')]")
            datos_jugador['liga'] = liga_element.text.strip()
        except:
            datos_jugador['liga'] = None
        
        # 14. Partidos jugados
        try:
            partidos_element = driver.find_element(By.XPATH, "//span[contains(@class, 'Text fftNCK')]")
            datos_jugador['partidos'] = partidos_element.text.strip()
        except:
            datos_jugador['partidos'] = None
        
        # 15. Valoración media
        try:
            valoracion_element = driver.find_element(By.XPATH, "//span[@aria-valuenow and @role='meter']")
            datos_jugador['valoracion_media'] = valoracion_element.get_attribute('aria-valuenow')
        except:
            datos_jugador['valoracion_media'] = None
        
        return datos_jugador
        
    except Exception as e:
        return {'url': jugador_url, 'error': str(e)}
    
    finally:
        if driver:
            driver.quit()

def worker_scraper():
    """Worker que procesa URLs de la cola"""
    container_id = os.environ.get('CONTAINER_ID', 'unknown')
    queue = JobQueue()
    monitor = MonitorSimple()
    monitor.iniciar()
    
    processed_count = 0
    
    print(f"Worker {container_id} iniciado")
    
    while True:
        # Obtener siguiente trabajo
        url = queue.get_job()
        
        if not url:
            print(f"No hay mas trabajos en la cola para worker {container_id}")
            time.sleep(5)
            continue
        
        try:
            print(f"Worker {container_id} procesando: {url}")
            
            # Actualizar métricas cada 10 procesados
            if processed_count % 10 == 0:
                monitor.actualizar()
            
            # Extraer datos
            datos = extraer_datos_jugador(url)
            
            if 'error' in datos:
                queue.save_error(f"{container_id}|{url}|{datos['error']}")
                print(f"Error en {url}: {datos['error']}")
            else:
                queue.save_result(f"{container_id}|{str(datos)}")
                print(f"Datos extraidos para {datos.get('nombre', 'Jugador desconocido')}")
            
            processed_count += 1
            
            # Pequeña pausa para evitar sobrecarga
            time.sleep(1)
            
        except Exception as e:
            queue.save_error(f"{container_id}|{url}|{str(e)}")
            print(f"Error general en worker {container_id}: {e}")
    
    monitor.finalizar()

def main():
    """Función principal"""
    if len(sys.argv) > 1 and sys.argv[1] == 'coordinator':
        # Modo coordinador: carga los trabajos
        print("Iniciando modo coordinador...")
        queue = JobQueue()
        
        # Leer URLs del archivo
        try:
            with open('jugadores_sofascore.csv', 'r') as f:
                urls = f.readlines()
            
            urls_to_process = urls[2000:2100]
            
            if queue.add_jobs(urls_to_process):
                print(f"{len(urls_to_process)} URLs cargadas en la cola")
                print("Coordinador terminado. Los workers pueden comenzar.")
            else:
                print("No se pudo conectar a Redis")
            
        except FileNotFoundError:
            print("No se encontro el archivo jugadores_sofascore.csv")
            sys.exit(1)
    
    else:
        # Modo worker: procesa trabajos
        worker_scraper()

if __name__ == "__main__":
    main()