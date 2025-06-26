#!/usr/bin/env python3
"""
Versión paralela del scraper para distribuir trabajo entre contenedores
"""

import pandas as pd
import os
import sys
from main import obtener_todos_datos_jugadores

def split_work(lista_jugadores, worker_id, total_workers):
    """Divide el trabajo entre múltiples workers"""
    chunk_size = len(lista_jugadores) // total_workers
    start_idx = (worker_id - 1) * chunk_size
    
    if worker_id == total_workers:
        # El último worker toma cualquier elemento restante
        end_idx = len(lista_jugadores)
    else:
        end_idx = start_idx + chunk_size
    
    return lista_jugadores[start_idx:end_idx]

def main():
    """Función principal para procesamiento paralelo"""
    worker_id = int(os.getenv('WORKER_ID', 1))
    total_workers = int(os.getenv('SCRAPER_WORKERS', 1))
    
    print(f"🔧 Worker {worker_id}/{total_workers} iniciando...")
    
    # Cargar lista completa de jugadores
    try:
        df_jugadores = pd.read_csv('/app/data/lista_jugadores.csv')
        lista_completa = df_jugadores['url'].tolist()
    except Exception as e:
        print(f"❌ Error cargando lista de jugadores: {e}")
        sys.exit(1)
    
    # Dividir trabajo
    mi_lista = split_work(lista_completa, worker_id, total_workers)
    print(f"📋 Worker {worker_id} procesará {len(mi_lista)} jugadores")
    
    # Ejecutar scraping
    datos, errores = obtener_todos_datos_jugadores(mi_lista)
    
    # Guardar resultado específico del worker
    df_resultado = pd.DataFrame(datos)
    output_path = f'/app/data/jugadores_worker_{worker_id}.csv'
    df_resultado.to_csv(output_path, index=False)
    
    print(f"✅ Worker {worker_id} completado. Datos guardados en {output_path}")

if __name__ == "__main__":
    main()