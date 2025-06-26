#!/usr/bin/env python3
"""
Aplicación principal para ejecutar el scraping de jugadores en contenedores Docker
"""

import pandas as pd
import numpy as np
import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup as bs

def obtener_todos_datos_jugadores(lista_jugadores):
    """
    Obtiene todos los datos de todos los jugadores
    """
    datos_jugadores = []
    errores = []
    
    for i, jugador_url in enumerate(lista_jugadores):
        print(f"Procesando jugador {i+1}/{len(lista_jugadores)}: {jugador_url}")
        
        try:
            options = Options()
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
            driver = webdriver.Chrome(options=options)
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            driver.get(jugador_url)
            wait = WebDriverWait(driver, 10)
            
            # Diccionario para almacenar datos del jugador
            datos_jugador = {
                'url': jugador_url,
                'nombre': 'No encontrado',
                'posicion': 'No encontrada',
                'equipo': 'No encontrado',
                'nacionalidad': 'No encontrada',
                'edad': 'No encontrada',
                'altura': 'No encontrada',
                'valor_mercado': 'No encontrado',
                'fisico': 'No encontrado',
                'velocidad': 'No encontrada',
                'tecnica': 'No encontrada',
                'tactica': 'No encontrada',
                'defensa': 'No encontrada',
                'creatividad': 'No encontrada',
                'liga': 'No encontrada',
                'partidos': 'No encontrada',
                'valoracion_media': 'No encontrado'
            }
            
            # 1. Nombre del jugador
            try:
                nombre_element = driver.find_element(By.XPATH, "//h1")
                datos_jugador['nombre'] = nombre_element.text.strip()
            except:
                pass
            
            # 2. Posición
            try:
                posicion_element = driver.find_element(By.XPATH, "//span[contains(@class, 'Text cVdAUM')]")
                datos_jugador['posicion'] = posicion_element.text.strip()
            except:
                pass
                
            # 3. Equipo
            try:
                equipo_element = driver.find_element(By.XPATH, "//div[contains(@class, 'Text dNnLfJ')]")
                datos_jugador['equipo'] = equipo_element.text.strip()
            except:
                pass
                
            # 4. Nacionalidad
            try:
                nacionalidad_element = driver.find_element(By.XPATH, "//div[contains(@class, 'Text esHnSj')]")
                datos_jugador['nacionalidad'] = nacionalidad_element.text.strip()
            except:
                pass
                
            # 5. Edad
            try:
                edad_element = driver.find_element(By.XPATH, "//div[contains(@class, 'Text fJTwFg')]")
                datos_jugador['edad'] = edad_element.text.strip()
            except:
                pass
                
            # 6. Altura
            try:
                altura_element = driver.find_element(By.XPATH, "//div[contains(@class, 'Text fJTwFg')]")
                datos_jugador['altura'] = altura_element.text.strip()
            except:
                pass
                
            # 7. Valor de mercado
            try:
                valor_element = driver.find_element(By.XPATH, "//div[contains(@class, 'Text dNnLfJ')]")
                datos_jugador['valor_mercado'] = valor_element.text.strip()
            except:
                pass
                
            # 8. Físico
            try:
                fisico_element = driver.find_elements(By.XPATH, "//span[contains(@class, 'textStyle_table.small c_surface.s1 lh_20px d_block ta_center')]")[0]
                datos_jugador['fisico'] = fisico_element.text.strip()
            except:
                pass
                
            # 9. Velocidad
            try:
                velocidad_element = driver.find_elements(By.XPATH, "//span[contains(@class, 'textStyle_table.small c_surface.s1 lh_20px d_block ta_center')]")[1]
                datos_jugador['velocidad'] = velocidad_element.text.strip()
            except:
                pass
                
            # 10. Técnica
            try:
                tecnica_element = driver.find_elements(By.XPATH, "//span[contains(@class, 'textStyle_table.small c_surface.s1 lh_20px d_block ta_center')]")[2]
                datos_jugador['tecnica'] = tecnica_element.text.strip()
            except:
                pass
                
            # 11. Táctica
            try:
                tactica_element = driver.find_elements(By.XPATH, "//span[contains(@class, 'textStyle_table.small c_surface.s1 lh_20px d_block ta_center')]")[3]
                datos_jugador['tactica'] = tactica_element.text.strip()
            except:
                pass
                
            # 12. Defensa
            try:
                defensa_element = driver.find_elements(By.XPATH, "//span[contains(@class, 'textStyle_table.small c_surface.s1 lh_20px d_block ta_center')]")[4]
                datos_jugador['defensa'] = defensa_element.text.strip()
            except:
                pass
                
            # 13. Creatividad
            try:
                creatividad_element = driver.find_elements(By.XPATH, "//span[contains(@class, 'textStyle_table.small c_surface.s1 lh_20px d_block ta_center')]")[5]
                datos_jugador['creatividad'] = creatividad_element.text.strip()
            except:
                pass
                
            # 14. Liga
            try:
                liga_element = driver.find_element(By.XPATH, "//div[contains(@class, 'Text gpUqFG')]")
                datos_jugador['liga'] = liga_element.text.strip()
                if datos_jugador['liga'] == datos_jugador['equipo']:
                    datos_jugador['liga'] = 'No encontrada'
            except:
                pass
                
            # 15. Partidos
            try:
                partidos_element = driver.find_element(By.XPATH, "//span[contains(@class, 'Text fftNCK')]")
                datos_jugador['partidos'] = partidos_element.text.strip()
            except:
                pass
                
            # 16. Valoración media
            try:
                valoracion_element = driver.find_element(By.XPATH, "//span[@aria-valuenow and @role='meter']")
                datos_jugador['valoracion_media'] = valoracion_element.get_attribute('aria-valuenow')
            except:
                pass
            
            datos_jugadores.append(datos_jugador)
            print(f"✅ Jugador procesado: {datos_jugador['nombre']}")
            
            driver.quit()
            time.sleep(2)  # Pausa entre requests

        except Exception as e:
            print(f"❌ Error en jugador {jugador_url}: {e}")
            errores.append({'url': jugador_url, 'error': str(e)})
            if 'driver' in locals():
                driver.quit()
            continue
    
    # Guardar resultado final
    df_final = pd.DataFrame(datos_jugadores)
    output_path = '/app/data/jugadores_datos_completos.csv'
    df_final.to_csv(output_path, index=False)
    
    print(f"\n🎉 Proceso completado!")
    print(f"✅ Jugadores procesados exitosamente: {len(datos_jugadores)}")
    print(f"❌ Errores encontrados: {len(errores)}")
    print(f"📁 Archivo guardado en: {output_path}")
    
    return datos_jugadores, errores

def main():
    """Función principal"""
    print("🚀 Iniciando scraping de jugadores...")
    
    # Lista de ejemplo de jugadores (puedes cargar desde un archivo)
    lista_jugadores = [
        'https://www.sofascore.com/football/player/tvardovskyi-denys/1127399',
        'https://www.sofascore.com/football/player/ladislav-almasi/825979'
    ]
    
    # También puedes cargar desde un archivo CSV
    try:
        if os.path.exists('/app/data/lista_jugadores.csv'):
            df_jugadores = pd.read_csv('/app/data/lista_jugadores.csv')
            lista_jugadores = df_jugadores['url'].tolist()
            print(f"📂 Cargados {len(lista_jugadores)} jugadores desde archivo")
    except Exception as e:
        print(f"⚠️  No se pudo cargar archivo de jugadores: {e}")
    
    # Ejecutar scraping
    datos, errores = obtener_todos_datos_jugadores(lista_jugadores)
    
    print("✨ Scraping completado")

if __name__ == "__main__":
    main()