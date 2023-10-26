import json
import requests
import time
from requests.exceptions import ProxyError
# import concurrent.futures

class ScraperHLibertad:
    def __init__(self, config):
        """Inicia el Scraper

        Args:
            config (dict): contiene las configuraciones: proxy, proxy_ip_port, output
        """
        self.config = config
        self.search_url = self.config['search_url']
        self.data = []
        self.actual_register = None
        self.session = requests.Session()
        if self.config['proxy']:
            self.session.proxies = config['proxy_ip_port']

    def fetch(self, url):
        """
        Realiza una solicitud HTTP a la URL especificada y devuelve la respuesta en formato json.
        """
        max_attempts = self.config['max_attempts'] 
        delay_attempts = self.config['delay_attempts']
        attempts = 0

        while attempts < max_attempts:
            try:
                response = self.session.get(url)
                if response.status_code == 200:
                    return response.json()
                else:
                    print(f"Error en la solicitud. Código de estado: {response.status_code}. Reintentando...")

            except ProxyError as e:
                print('Error de proxy:', e)
                return None
            except requests.RequestException as e:
                print(f"Error de solicitud: {e}. Reintentando...")

            attempts += 1
            print(f"Reintentando. quedan {max_attempts-attempts} intentos'")
            time.sleep(delay_attempts)

        print(f"No se pudo hacer el request a: {url}. Fin de intentos")
        return None
    
    def run(self):
        """ Ejecución del codigo
        """
            
        # with concurrent.futures.ThreadPoolExecutor(max_workers=self.config['numero_hilos']) as executor:
        #     executor.map(, lista_registros)

        self.close()
    
    def obtener_categorias(self):
        """Obtener la lista de categorias y darles el formato para el procesamiento
        """
        pass


    def crear_csv(self):
        """
        Convierte los datos extraídos en formato JSON.
        """
        pass

    def close(self):
        """
        Cerrar la sesion
        """
        self.session.close()