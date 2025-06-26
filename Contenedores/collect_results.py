import redis
import pandas as pd
import ast
import time
import sys
import json

class ResultsCollector:
    def __init__(self, redis_host='redis', redis_port=6379):
        try:
            self.redis_client = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)
            self.redis_client.ping()
        except:
            print("No se pudo conectar a Redis")
            self.redis_client = None
            
        self.results_key = 'scraping_results'
        self.errors_key = 'scraping_errors'
    
    def collect_results(self):
        """Recolecta todos los resultados y los guarda en archivos"""
        if not self.redis_client:
            return 0, 0
            
        print("Iniciando recoleccion de resultados...")
        
        # Recolectar resultados exitosos
        results = []
        while True:
            result = self.redis_client.rpop(self.results_key)
            if not result:
                break
            
            try:
                # Parsear el resultado
                parts = result.split('|', 1)
                if len(parts) == 2:
                    container_id, data_str = parts
                    # Convertir string a diccionario
                    data = ast.literal_eval(data_str)
                    data['processed_by'] = container_id
                    results.append(data)
            except Exception as e:
                print(f"Error parseando resultado: {e}")
        
        # Recolectar errores
        errors = []
        while True:
            error = self.redis_client.rpop(self.errors_key)
            if not error:
                break
            
            try:
                parts = error.split('|', 2)
                if len(parts) == 3:
                    container_id, url, error_msg = parts
                    errors.append({
                        'container_id': container_id,
                        'url': url,
                        'error': error_msg
                    })
            except Exception as e:
                print(f"Error parseando error: {e}")
        
        # Guardar resultados
        if results:
            df_results = pd.DataFrame(results)
            df_results.to_csv('/app/results/jugadores_datos_completos.csv', index=False)
            print(f"{len(results)} resultados guardados en jugadores_datos_completos.csv")
        
        if errors:
            df_errors = pd.DataFrame(errors)
            df_errors.to_csv('/app/results/jugadores_errores.csv', index=False)
            print(f"{len(errors)} errores guardados en jugadores_errores.csv")
        
        # Estadísticas
        if results or errors:
            print("\n" + "="*60)
            print("ESTADISTICAS ACTUALES")
            print("="*60)
            print(f"Resultados exitosos: {len(results)}")
            print(f"Errores encontrados: {len(errors)}")
            
            if results:
                # Estadísticas por container
                containers = {}
                for result in results:
                    container = result.get('processed_by', 'unknown')
                    containers[container] = containers.get(container, 0) + 1
                
                print("\nResultados por worker:")
                for container, count in containers.items():
                    print(f"  {container}: {count} jugadores")
            
            print("="*60)
        
        return len(results), len(errors)

def main():
    collector = ResultsCollector()
    
    if not collector.redis_client:
        print("No se puede ejecutar sin Redis")
        sys.exit(1)
    
    print("Esperando resultados... (Ctrl+C para finalizar)")
    
    try:
        while True:
            time.sleep(30)  # Recolectar cada 30 segundos
            success_count, error_count = collector.collect_results()
            
            if success_count == 0 and error_count == 0:
                print(f"No hay nuevos resultados... {time.strftime('%H:%M:%S')}")
            
    except KeyboardInterrupt:
        print("\nFinalizando recoleccion...")
        collector.collect_results()
        print("Recoleccion finalizada")

if __name__ == "__main__":
    main()