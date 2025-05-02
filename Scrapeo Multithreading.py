import requests
from bs4 import BeautifulSoup
import csv
import time
import random
import os
import concurrent.futures
from datetime import datetime
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f"transfermarkt_scraper_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Configuración global
MAX_WORKERS = min(32, os.cpu_count() * 4)  # Máximo de hilos (4x núcleos de CPU, máximo 32)
REQUEST_TIMEOUT = 10  # Segundos
MIN_REQUEST_DELAY = 0.5  # Segundos mínimos entre solicitudes
MAX_REQUEST_DELAY = 2.0  # Segundos máximos entre solicitudes

def extraer_letras_con_espacios(texto):
    """Extrae solo letras y espacios de un string."""
    return ''.join(c for c in texto if c.isalpha() or c.isspace())

def scrape_player_data(player_id):
    """Extrae datos de un jugador de Transfermarkt usando su ID."""
    url = f'https://www.transfermarkt.pe/player-name/leistungsdaten/spieler/{player_id}'
    start_time = time.time()
    logger.info(f"Iniciando extracción de jugador ID {player_id}")
   
    # Agregar retraso aleatorio para evitar ser bloqueado
    time.sleep(random.uniform(MIN_REQUEST_DELAY, MAX_REQUEST_DELAY))
   
    # Headers con diferentes User-Agents para evitar ser bloqueado
    headers = {
        'User-Agent': random.choice([
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0'
        ])
    }
   
    # Realizar la solicitud
    try:
        response = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logger.error(f"Error al obtener datos para el jugador ID {player_id}: {e}")
        return {'id': player_id, 'error': str(e)}
   
    # Parsear el contenido HTML
    soup = BeautifulSoup(response.content, 'html.parser')
   
    # Verificar si la página existe
    if "No se ha encontrado la página" in soup.text or "Page not found" in soup.text:
        logger.warning(f"Jugador con ID {player_id} no encontrado")
        return {'id': player_id, 'error': 'Player not found'}
   
    # Diccionario para almacenar datos del jugador
    player_data = {'id': player_id}
   
    try:
        # Extraer datos básicos
        dorsal_element = soup.find('span', class_='data-header__shirt-number')
        player_data['dorsal'] = dorsal_element.text.strip() if dorsal_element else 'N/A'
       
        nombre_element = soup.find('h1', class_='data-header__headline-wrapper')
        if nombre_element:
            raw_name = nombre_element.text.strip()
            player_data['nombre'] = extraer_letras_con_espacios(raw_name)
        else:
            player_data['nombre'] = 'N/A'
       
        # Obtener datos de los elementos data-header__content
        data_contents = soup.find_all('span', class_='data-header__content')
       
        content_mapping = {
            'nacionalidad': 5,
            'edad': 3,
            'altura': 6,
            'posicion': 7
        }
       
        for key, idx in content_mapping.items():
            try:
                player_data[key] = data_contents[idx].text.strip() if len(data_contents) > idx else 'N/A'
            except (AttributeError, IndexError):
                player_data[key] = 'N/A'
       
        # Datos internacionales
        intl_app = soup.find('a', class_='data-header__content data-header__content--highlight')
        player_data['partidos_internacional'] = intl_app.text.strip() if intl_app else '0'
       
        intl_goals = soup.find_all('a', class_='data-header__content data-header__content--highlight')
        player_data['goles_internacional'] = intl_goals[1].text.strip() if len(intl_goals) > 1 else '0'
       
        # Valor de mercado y club
        market_value_element = soup.find('a', class_='data-header__market-value-wrapper')
        player_data['valor_mercado'] = market_value_element.text.strip() if market_value_element else 'N/A'
       
        club_element = soup.find('span', class_='data-header__club')
        player_data['club'] = club_element.text.strip() if club_element else 'N/A'
       
        liga_element = soup.find('span', class_='data-header__league')
        player_data['liga'] = liga_element.text.strip() if liga_element else 'N/A'
       
        # Estadísticas
        zentriert_cells = soup.find_all('td', class_='zentriert')
        rechts_cells = soup.find_all('td', class_='rechts')
       
        player_data['partidos_jugados'] = zentriert_cells[0].text.strip() if zentriert_cells else 'N/A'
        player_data['goles'] = zentriert_cells[1].text.strip() if len(zentriert_cells) > 1 else 'N/A'
        player_data['asistencias'] = zentriert_cells[2].text.strip() if len(zentriert_cells) > 2 else 'N/A'
        player_data['minutos_jugados'] = rechts_cells[1].text.strip() if len(rechts_cells) > 1 else 'N/A'
       
        # Agregar tiempo de proceso
        player_data['tiempo_proceso'] = time.time() - start_time
       
        logger.info(f"✓ Datos extraídos para {player_data.get('nombre', f'Jugador ID {player_id}')} en {player_data['tiempo_proceso']:.2f}s")
        return player_data
   
    except Exception as e:
        logger.error(f"Error al procesar datos del jugador ID {player_id}: {e}")
        return {'id': player_id, 'error': str(e)}

def main():
    start_time = time.time()
    logger.info(f"=== INICIANDO EXTRACCIÓN DE DATOS DE TRANSFERMARKT ===")
    logger.info(f"Usuario: paolosalazarp")
    logger.info(f"Fecha y hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"Usando {MAX_WORKERS} hilos")
   
    # Configuración
    start_id = 1  # ID de inicio
    end_id = 1000  # ID final
   
    # Generar lista de IDs
    player_ids = list(range(start_id, end_id + 1))
   
    # Lista para almacenar resultados
    all_results = []
   
    # Usar ThreadPoolExecutor para procesar en paralelo
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        # Enviar todas las tareas al executor
        future_to_id = {executor.submit(scrape_player_data, player_id): player_id for player_id in player_ids}
       
        # Procesar resultados a medida que se completan
        for i, future in enumerate(concurrent.futures.as_completed(future_to_id)):
            player_id = future_to_id[future]
            try:
                data = future.result()
                all_results.append(data)
               
                # Mostrar progreso
                completed = i + 1
                logger.info(f"Progreso: {completed}/{len(player_ids)} jugadores procesados ({completed/len(player_ids)*100:.1f}%)")
               
            except Exception as e:
                logger.error(f"Error al procesar future para jugador ID {player_id}: {e}")
                all_results.append({'id': player_id, 'error': f"Future exception: {str(e)}"})
   
    # Guardar resultados en CSV
    csv_filename = f'transfermarkt_players_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
   
    # Obtener todos los campos únicos
    fieldnames = set()
    for player in all_results:
        fieldnames.update(player.keys())
    fieldnames = sorted(list(fieldnames))
   
    # Escribir CSV
    with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_results)
   
    # Estadísticas finales
    total_time = time.time() - start_time
    success_count = sum(1 for r in all_results if 'error' not in r)
   
    logger.info("\n" + "=" * 50)
    logger.info(f"=== RESUMEN DE LA EXTRACCIÓN ===")
    logger.info("=" * 50)
    logger.info(f"Tiempo total: {total_time:.2f} segundos ({total_time/60:.2f} minutos)")
    logger.info(f"Jugadores procesados: {len(player_ids)}")
    logger.info(f"Jugadores con datos exitosos: {success_count}")
    logger.info(f"Jugadores con errores: {len(player_ids) - success_count}")
    logger.info(f"Tasa de éxito: {success_count/len(player_ids)*100:.2f}%")
    logger.info(f"Tiempo promedio por jugador: {total_time/len(player_ids):.2f} segundos")
    logger.info(f"Archivo: {csv_filename}")
    logger.info("=" * 50)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.warning("Extracción interrumpida por el usuario")
    except Exception as e:
        logger.critical(f"Error crítico en la aplicación: {e}")