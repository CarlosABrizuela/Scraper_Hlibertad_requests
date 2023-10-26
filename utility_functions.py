import yaml
import os

main_dir = os.path.dirname(__file__)
def get_config():
    """
    Obtiene los datos de configuracion del archivo /file/config.yml
    """
    file_path = os.path.join(main_dir, 'files', 'config.yaml')
    try:
        with open(file_path, "r") as config_file:
            config = yaml.safe_load(config_file)
            return config
    except FileNotFoundError as e:
        print(f"El archivo no se encontró. {e.filename}")
        config = {}
        config["search_url"]= "https://www.hiperlibertad.com.ar/api/catalog_system/pub/products/search"
        config["proxy"]= False
        config['thread_number']= 5
        config['max_attempts']= 2
        config['delay_attempts']= 5
        return config
    