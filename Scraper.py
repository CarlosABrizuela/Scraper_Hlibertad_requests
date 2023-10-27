import requests
import time
from requests.exceptions import ProxyError
import concurrent.futures
from urllib.parse import urlparse, parse_qs
from datetime import datetime
import csv
import pandas as pd
from utility_functions import CONSOLE

class ScraperHLibertad:
    def __init__(self, config):
        """Start the Scraper

        Args:
            config (dict): it has the configurations: proxy, proxy_ip_port, output
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
                if response.ok:
                    return response.json()
                else:
                    CONSOLE.info(f"Request not ok. Status code: {response.status_code}.")

            except ProxyError as e:
                CONSOLE.error('Proxy error:', e)
                return None
            except requests.RequestException as e:
                CONSOLE.error(f"Request error: {e}.")

            attempts += 1
            CONSOLE.info(f"Retrying. >{max_attempts-attempts} attempts lefts'")
            time.sleep(delay_attempts)

        CONSOLE.info(f"The request could not be made: {url}. No more attempts")
        return None
    
    def run(self):
        """ main method. 
        """
        all_categories = self.get_categories()
        if not all_categories: return
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.config['thread_number']) as executor:
            executor.map(self.process_department, all_categories)

        self.close()
    
    def process_department(self, department):
        """Obtain the products for each category or department (level 1 category)
        """
        for sub_category in department['sub_categorias']:
            self.process_subcategory(sub_category)
        
        self.crear_csv(department['nombre'])

    def process_subcategory(self, sub_category):
        """get all products for every category in the current deparment
        sub={
            'nombre':'', codigo:''
        }
        """
        param_categories = f"?fq=C:/{sub_category['codigo']}"
        _from = 1
        _to = self.config['pagination']
        # lista= []
        while True:
            pagination= f"&_from={_from}&_to={_to}"
            url= f"{self.search_url}{param_categories}{pagination}"
            products= self.fetch(url)
            if not products: break
            for product in products:
                self.process_product(product)

            _from += _to
            _to+= _to

    def process_product(self, product):
        """ extract the product information """
        try:
            dict_prod= {
            'nombre': product['productName'],
            'precio_publicado': product['items'][0]['sellers'][0]['commertialOffer']['PriceWithoutDiscount'],
            'precio_regular': product['items'][0]['sellers'][0]['commertialOffer']['ListPrice'], #precio tachado
            'categoria': product['categories'][0],
            'SKU': self.get_sku_from_product(product['items'][0]['sellers'][0]['addToCartLink']),
            'url_producto': product['link'],
            'stock': product['items'][0]['sellers'][0]['commertialOffer']['AvailableQuantity'],
            'descripcion': str(product['description']).replace('\n', ' ').replace('\r', '') # quitamos los espacios
            }
            self.data.append(dict_prod)
        except Exception as e:
            CONSOLE.info(f'(Process product): {e}')
        
    def get_sku_from_product(self, url):
        """ extract the sku value from the 'addToCart' link"""
        parsed_url = urlparse(url)
        query_parameters = parse_qs(parsed_url.query)
        sku = query_parameters.get("sku", None)
        if sku:
            return sku[0]
        else:
            return None
        
    def get_categories(self):
        """Get the list of categories and format them for processing
         We need codigo to use in the query.
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

    def process_list_categories(self, categories_json):
        """ accumulates the last level categories in a list, for each first level category. """
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
        """ Returns the leaf categories, or those that do not have child categories. """
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

    def crear_csv(self, category_name):
        """
            To create the csv file with the products.
        """
        date = (datetime.today()).strftime('%d-%m-%Y')
        df = pd.DataFrame(self.data)
        ouput= f'{date}__{category_name}.csv'
        df.to_csv(f'{self.config['output_dir']}/{ouput}',  quoting=csv.QUOTE_MINIMAL)
        CONSOLE.info(f"* A new output file was generated: {ouput}")

    def close(self):
        """
        Close the session
        """
        self.session.close()