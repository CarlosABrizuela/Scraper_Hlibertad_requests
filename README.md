![hiper libertad](https://hiperlibertad.vtexassets.com/assets/vtex/assets-builder/hiperlibertad.fizzmod-theme/1.17.1/img/retailStoreLogo___647637fa923edf985acb24aa6915109e.svg)
# auto_scraping_libertad
Scraping test challenge for AUTOscraping. Using Requests library to the vtex api.

Page: _hiperlibertad.com.ar_

Version of python: **Python 3.12.0**, Request library.
The main goal is to get all products from the page and save them into csv files, one for every category, for every branch.

API reference: 
- [How search parameters work](https://developers.vtex.com/docs/guides/how-search-parameters-work)
- [Search for Products with Filter, Order and Pagination](https://developers.vtex.com/docs/api-reference/search-api#get-/api/catalog_system/pub/products/search)

### To achieve this, first we get the list of categories from the website, then format that as follows
```json
[
    {
        "nombre": "Tecnologia",
        "sub_categorias": [
            {
                "nombre": "Tecnologia/TV Y VIDEO/TV LED Y SMART TV",
                "codigo": "1/33/34"
            },"..."
    }
    "..."
]
```
### We use codigo to form the url.
Search url: https://www.hiperlibertad.com.ar/api/catalog_system/pub/products/search
Pagination:

Initial item number - _from={{first}}

Final item number - _to={{last}}

Category: ?fq=C:[DepartmentId/CategoryId/SubcategoryId]

Ending up like this:
https://www.hiperlibertad.com.ar/api/catalog_system/pub/products/search?&fq=C:{id-cat-1}/{id-cat2}/{id-cat-3}&_from={from}&_to={to}

It returns a json file with add products information that we paginate through this every 10 (configurable) products.

- Output format: **date**__**category-name****.csv**
>'31-10-2023__Tecnologia.csv'

### To config the script it was used a yaml file: 'config.yaml'
> [!NOTE]
> Change before run.
```yaml
search_url: https://www.hiperlibertad.com.ar/api/catalog_system/pub/products/search  #API search url
categories_url: https://www.hiperlibertad.com.ar/api/catalog_system/pub/category/tree/3 # url to categories json file.
proxy: False     # indicate if proxy will be use to connect.
proxy_ip_port:      # proxy port example: 35.236.207.242:33333
thread_number: 5    # number of threads
max_attempts: 2     # number of attempts if a connection could not be established.
delay_attempts: 3   # waiting seconds in every attempt
pagination: 10      # number of products for each page.
output_dir: C:\Users\salida  # folder dir where files will be saved (it must exist)
```
## Libraries
- [requests](https://requests.readthedocs.io/): to make http requets.
- [PyYAML](https://pyyaml.org/): To manage the configuration.
- [pandas](https://pandas.pydata.org/docs/index.html): To create the csv files.

## How to use:
- Clone the project
```
git clone https://github.com/CarlosABrizuela/Scraper_Hlibertad_requests.git
```
```
cd Scraper_Hlibertad_requests
```
- Install the libraries
```
pip install -r requirements.txt
```
- run the script
```
python main.py
```

## Licencia
- Sin Licencia