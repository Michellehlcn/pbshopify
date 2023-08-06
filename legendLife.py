# Using Selenium WebDriver 2

from bs4 import BeautifulSoup as bs
import requests
import json 
import re
import time
import logging
import base64
import pandas as pd

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

token =""
store=""
location=""
def getCollectionLink(driver):
    page = 1
    dic = []
    while page <11:
        driver.get(f"https://www.legendlife.com.au/product_search?limit=100&p={page}")
        products = driver.find_element(By.CLASS_NAME, "products-grid")
        itm = products.find_elements(By.TAG_NAME, 'li')
        for i in range(1,2):
            pag = {}
            product = products.find_element(By.CSS_SELECTOR, f"li:nth-of-type({i})").find_element(By.CLASS_NAME, "product-code" ).find_element(By.TAG_NAME, 'a')
            link = product.get_attribute("href")
            title = product.get_attribute("title")
            sku = product.text
            price = products.find_element(By.CSS_SELECTOR, f"li:nth-of-type({i})").find_element(By.CLASS_NAME, "regular-price").find_element(By.CLASS_NAME, "price").text
          
            pag["sku"] = sku
            pag["link"] = link
            pag["title"] = title
            pag["lowest_price"] = price
            pag["tags"] = "new"
            dic.append(pag)
        page += 1
    print(dic)
    return dic  


def getData(url, driver):
    driver.get(url)

    driver.find_element(By.ID,"colour-selector-dropdown").click()
    dropdown = Select(driver.find_element(By.ID,"attribute137"))
    fulldata = []
    for i in (1,len(dropdown.options)-1):

        dropdown.select_by_value(dropdown.options[i].get_attribute("value"))
        time.sleep(4)
        html = driver.page_source
        table = driver.find_element(By.ID, "order-summary-row-table-id")
        if (table.find_element(By.CSS_SELECTOR, "tr:nth-of-type(1)").find_element(By.CSS_SELECTOR, "td:nth-of-type(1)" ).text =="Size"):
            for tr in range(2,10):
                try:
                    data = {}
                    data["color"] = dropdown.options[i].text
                    data["size"] = table.find_element(By.CSS_SELECTOR, f"tr:nth-of-type({tr})").find_element(By.CSS_SELECTOR, "td:nth-of-type(1)" ).text
                    data["stock"] = table.find_element(By.CSS_SELECTOR,f"tr:nth-of-type({tr})").find_element(By.CSS_SELECTOR, "td:nth-of-type(2)" ).text
                    
                    fulldata.append(data)
                except Exception as e:
                    continue
        else:
            data = {}
            data["color"] = dropdown.options[i].text
            data["size"] =""
            data["stock"] = table.find_element(By.CSS_SELECTOR, "tr:nth-of-type(2)").find_element(By.CSS_SELECTOR, "td:nth-of-type(1)" ).text
           
            fulldata.append(data)
    print(fulldata)
    return fulldata


class scrapeData():
    def setUp(self):
        self.driver = webdriver.Firefox()
    def login(self):
        driver = self.driver
        driver.get(URL)
        self.assertIn("search", driver.title)
        
        username = driver.find_element(By.ID, "email")
        password = driver.find_element(By.ID, "password")
        username.send_keys(e)
        password.send_keys(p)
        driver.find_element(By.ID,"send2").click()
if __name__ == "__main__":
    scrapeData()
def remove_empty_lists (lst):
    return [ e for e in lst if len(e)!=0]

def createNewProducts(data, colorList, sizeList):
    print(colorList)
    print(sizeList)
    variant = data["variants"][0]
    colorList = [*set(colorList)]
    sizeList = [*set(remove_empty_lists(sizeList))]
    print(colorList)
    print(sizeList)
    print(len(sizeList))
    url = f"https://{store}/admin/api/2023-07/products.json"
    if len(sizeList) != 0 :
        payload = {
            "product": {
                "title": f'{data["sku"]}.{data["title"]}',
                "body_html": data["description"],
                "vendor": "Legend Life",
                "status": "draft",
                "published_scope": "web",
                "tags": data["tags"],
                 "variant": { 
                    "title": f'{variant.get("color")} {variant.get("size")}', 
                    "option1": variant.get("color"),
                    "option2": variant.get("size"),
                    "sku":  f'{data["sku"]}.{variant.get("color")}.{variant.get("size")}',
                    "price": re.sub("[^\d\.]","",str(data["lowest_price"])),
                    "inventory_management": "shopify"
                },
                "options":[{
                    "name":"Color",
                    "values":colorList
                    },{
                    "name": "Size",
                    "values":sizeList
                    }
                ]
            }}
    else:
        payload = {
        "product": {
            "title": data["title"],
            "body_html": data["description"],
            "vendor": "Legend Life",
            "status": "draft",
            "published_scope": "web",
            "tags": data["tags"],
             "variant": {   
                    "title": variant.get("color"), 
                    "option1": variant.get("color"),
                    "sku": f'{data["sku"]}.{variant.get("color")}',
                    "price": re.sub("[^\d\.]","",str(data["lowest_price"])),
                    "inventory_management": "shopify"
            },
            "options":[{
                "name":"Color",
                "values":colorList
                }
            ]
        }}
    headers = {
        "Content-Type": "application/json",
        "X-Shopify-Access-Token": token,
        "Accept": "aplication/json"
    }

    response = requests.request("POST", url, json=payload, headers=headers)
    products = json.loads(response.text)
    return products
def encodeFile(link):
    return base64.b64encode(requests.get(link).content).decode('utf-8')

def addImage(id, links):
    print(links)
    payload = []
    for link in links:

        print(link)
        payload={
            "image": {
                "attachment": encodeFile(link)
            }
        }
        url = f'https://{store}/admin/api/2023-07/products/{id}/images.json'
        headers = {
            "Content-Type": "application/json",
            "X-Shopify-Access-Token": token,
            "Accept": "aaplication/json"
        }
        response = requests.request("POST", url, json=payload, headers=headers)
def addStockVariant(productId, variantId, variant, product): 
   
    url = f'https://{store}/admin/api/2023-07/products/{productId}.json'
    if variant.get('size') != "":
        #Has size
        payload = {
            "product": {
                "variant": {
                    "id": variantId,     
                    "title": f'{variant.get("color")} {variant.get("size")}', 
                    "option1": variant.get("color"),
                    "option2": variant.get("size"),
                    "sku":  f'{product["sku"]}.{variant.get("color")}.{variant.get("size")}',
                    "price": re.sub("[^\d\.]","",str(product["lowest_price"])),
                    "inventory_management": "shopify"
                }
            }
        }
    else: 
        #No size
        payload = {
            "product": {
                "variant": {
                    "id": variantId,     
                    "title": variant.get("color"), 
                    "option1": variant.get("color"),
                    "sku": f'{product["sku"]}.{variant.get("color")}',
                    "price": re.sub("[^\d\.]","",str(product["lowest_price"])),
                    "inventory_management": "shopify"
                }
            }
        }
  
    headers = {
        "Content-Type": "application/json",
        "X-Shopify-Access-Token": token,
        "Accept": "aplication/json"
    }

    response = requests.request("PUT", url, json=payload, headers=headers)
    print(f'>> response Add stock variant {response.status_code}')
    variant = json.loads(response.text)
    return variant
def addNewStockVariant(productId, variant, product): 
    url = f'https://{store}/admin/api/2023-07/products/{productId}/variants.json'
    if variant.get('size') != "":
        payload = {
            "variant": {    
                "sku": f'{product["sku"]}.{variant.get("color")}.{variant.get("size")}',
                "title": f'{variant.get("color")} {variant.get("size")}', 
                "option1": variant.get("color"),
                "option2": variant.get("size"),
                "price": re.sub("[^\d\.]","",str(product["lowest_price"])),
                "inventory_management": "shopify"
            }}
    else:
        payload = {
        "variant": {    
            "sku":f'{product["sku"]}.{variant.get("color")}',
            "title": variant.get("color"),
            "option1": variant.get("color"),
            "price": re.sub("[^\d\.]","",str(product["lowest_price"])),
            "inventory_management": "shopify"
    }}
    headers = {
        "Content-Type": "application/json",
        "X-Shopify-Access-Token": token,
        "Accept": "aplication/json"
    }

    response = requests.request("POST", url, json=payload, headers=headers)
    print(f'>>  response Add new stock variant {response.status_code}')
   
    variant = json.loads(response.text)
    return variant
def addInventoryLevel(inventoryId, avail):
    print(f'{str(inventoryId)} - stock level: {avail}')
    if avail is None:
        avail = '0'
    url = f'https://{store}/admin/api/2023-07/inventory_levels/set.json'
    payload = {
        "location_id": location,
        "inventory_item_id": inventoryId,
        "available": re.sub("[+,]","",avail),
    }
    headers = {
        "Content-Type": "application/json",
        "X-Shopify-Access-Token": token,
        "Accept": "aplication/json"
    }

    response = requests.request("POST", url, json=payload, headers=headers)


# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO, filename='log.log')

logger = logging.getLogger(__name__)

e=""
p=""
URL="https://www.legendlife.com.au/customer/account/login/referer/aHR0cHM6Ly93d3cubGVnZW5kbGlmZS5jb20uYXUvY3VzdG9tZXIvYWNjb3VudC9pbmRleC8,/"
driver = webdriver.Firefox()
driver.get(URL)
# assertIn("search", driver.title)
wait = WebDriverWait(driver, 20)
username = driver.find_element(By.ID, "email")
password = driver.find_element(By.ID, "pass")
username.send_keys(e)
password.send_keys(p)
driver.find_element(By.ID,"send2").click()
items = getCollectionLink(driver)
for item in items:
    variant = getData(item.get("link"), driver)
    item["variants"] = variant
    print(variant)
    item["description"] = driver.find_element(By.CLASS_NAME, "short-description" ).text
    print(item["description"])
    images = driver.find_element(By.CLASS_NAME, "swatchesContainer" ).find_elements(By.TAG_NAME,"a") 
    item["product_image"] = [image.get_attribute('href') for image in images]
print(items)
products = items

for i in range(len(products)):
    colorList = [p.get('color') for p in products[i]["variants"]]
    sizeList = [p.get('size') for p in products[i]["variants"]]
    pr = createNewProducts(products[i], colorList, sizeList)
    print(pr)
    time.sleep(1)
    # Add image
    addImage(pr["product"]['id'], products[i]["product_image"])
    time.sleep(1)
    
    # if product item only have one variant, modify exiting variant
    # if product item has more than one variant, modify the first variant and create new variants for the rest of the list
    print(products[i]["variants"])

    for j in range(len(products[i]["variants"])):
        if j == 0:   
            vr = addStockVariant(pr['product']['id'], pr["product"]['variants'][0]['id'], products[i]["variants"][j], products[i])
            time.sleep(1)
            addInventoryLevel(vr["product"]["variants"][0]["inventory_item_id"],products[i]["variants"][j]["stock"])
            time.sleep(1)
        if j > 0:
            vr = addNewStockVariant(pr["product"]["id"], products[i]["variants"][j], products[i])
            time.sleep(1)
            print(vr)
            addInventoryLevel(vr["variant"]["inventory_item_id"],products[i]["variants"][j]["stock"])
            time.sleep(1)