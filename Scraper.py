from sre_parse import CATEGORIES
import requests
import time
from requests.exceptions import ProxyError
import concurrent.futures

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
        """ main method. 
        """
        all_categories = self.get_categories()
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.config['thread_number']) as executor:
            executor.map(self.process_category, all_categories)

        self.close()
    
    def process_category(self, category):
        """Obtener los productos para cada categoria
        """
        print(category['nombre'])

    def get_categories(self):
        """Obtener la lista de categorias y darles el formato para el procesamiento
        Necesitamos el codigo para usar en la consulta.
        formato:
        {
            "nombre": "Tecnologia",
            "sub_categorias": [
                    {
                        "nombre": "Tecnologia/TV Y VIDEO/TV LED Y SMART TV",
                        "codigo": "1/33/34"
                    }, ...
                ], ...
        }
        """
        categories_json = self.fetch(self.config['categories_url'])
        if categories_json:
            return self.process_list_categories(categories_json)
        # else:
        #     return self.process_list_categories(get_local_categories())

    def process_list_categories(self, categories_json):
        # acumula en una lista las categorias de ultimo nivel, para cada categoria de primer nivel.
        lista_sup= []
        for category in categories_json:
            sub_categories = []
            if category["hasChildren"]:
                nombre = category["name"]
                codigo = str(category["id"])
                self.process_list_subcategories(category["children"], sub_categories, nombre, codigo)

            categoria_dict_sup ={
                    "nombre": category['name'],
                    "sub_categorias": sub_categories
                }
            lista_sup.append(categoria_dict_sup)
            
        return lista_sup

    def process_list_subcategories(self, categorias_json, list_subcats, nombre, codigo):
        # Devuelve las categorias hojas, o esas que no tienen categorias hijas.
        nombre_prev =nombre
        codigo_prev = codigo
        for index, categoria in enumerate(categorias_json):
            nombre = nombre +"/"+ categoria["name"]
            codigo = codigo +"/"+ str(categoria["id"])
            if categoria["hasChildren"]:
                self.process_list_subcategories(categoria["children"], list_subcats, nombre, codigo)
            else:
                categoria_dict = {
                    "nombre": nombre,
                    "codigo": codigo
                }
                list_subcats.append(categoria_dict)
            nombre = nombre_prev
            codigo = codigo_prev
        
            if index == len(categorias_json) - 1:
                return

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