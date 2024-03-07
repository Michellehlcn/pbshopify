
#-------------------------------------------------------------------------------

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.chrome.options import Options 
# import logging
import undetected_chromedriver as uc
import ssl
import requests
import json 
import re
import time
import base64
import os
ssl._create_default_https_context = ssl._create_unverified_context

import time
import math

token=""
store=""
location="" 
# Enable logging

# logging.basicConfig(
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
#     level=logging.INFO, filename='benchmark.log')

# logger = logging.getLogger(__name__)
URL=""
e=''
p=''
url_ = ""
link1 =""
link2 =""
link3=""

sub1 = ""

winning_spirit_subs =[]
winning_spirit_cat_url = []
winning_spirit_items = []



def appendItemLink (driver, cat):
    global winning_spirit_items
    cat_ = driver.find_elements(By.CLASS_NAME, "facets-item-cell-grid-link-image")
    # number = driver.find_element(By.CSS_SELECTOR, "h1").get_attribute("data-quantity")
    # print(number)
    for _ in cat_:
        item_link =_.get_attribute("href")
        print(f'{item_link}')
        winning_spirit_items.append({"cat": cat, "url": item_link})

def getItemLink(driver, link1, collection):
    global winning_spirit_cat_url
    global winning_spirit_subs
    global winning_spirit_items

    collection = "winning-spirit"
    driver.get(link1)
    time.sleep(5)
    sub = driver.find_element(By.ID,"content").find_element(By.CLASS_NAME,"category-subcategories")
    itm = sub.find_elements(By.TAG_NAME, 'li')
    print(len(itm))

    for i in range(1,len(itm)+1):
        tag = sub.find_element(By.CSS_SELECTOR, f"li:nth-of-type({i})").find_element(By.TAG_NAME, "a").get_attribute("href")
        print(f'{tag}')
        winning_spirit_subs.append(tag)
    for i_ in winning_spirit_subs:
        sub_collection = i_.split("/")[-1]
        driver.get(i_)
        time.sleep(5)
        items = driver.find_element(By.ID,"content").find_element(By.ID, "facet-browse").find_element(By.CLASS_NAME, "facets-facet-browse-facets-sidebar").find_element(By.CLASS_NAME,"facets-faceted-navigation-item-category").find_element(By.CLASS_NAME, "facets-faceted-navigation-item-category-facet-group").find_element(By.CLASS_NAME,"facets-faceted-navigation-item-category-facet-group-wrapper").find_element(By.CLASS_NAME, "facets-faceted-navigation-item-category-facet-group-content").find_element(By.CLASS_NAME, "facets-faceted-navigation-item-category-facet-optionlist")
        itm_sub = items.find_elements(By.TAG_NAME, "li")
        print(len(itm_sub))
        for x in range(1, len(itm_sub)+1):
            tag_sub = items.find_element(By.CSS_SELECTOR, f"li:nth-of-type({x})").find_element(By.TAG_NAME, "a").get_attribute("href")
            print(f'{tag_sub}')
            winning_spirit_cat_url.append(tag_sub)
    for cat in winning_spirit_cat_url:
        driver.get(cat)
        time.sleep(5)
        number = driver.find_element(By.CLASS_NAME, "facets-facet-browse-title").get_attribute("data-quantity")
        print(int(number))
        cat_ = driver.find_elements(By.CLASS_NAME, "facets-item-cell-grid-link-image")

        for _ in cat_:
            item_link =_.get_attribute("href")
            print(f'{item_link}')
            winning_spirit_items.append({"cat": cat,"url": item_link})
        
        if int(number) >24:
            # going to second page
            page_max = math.floor(int(number)/24)
            for page in range(2,page_max+1):
                driver.get(f'{cat}?page={page}')
                time.sleep(5)
                appendItemLink(driver, cat)

def scrapeItem(driver, url, collection, sub, category):
    print(url)
    driver.get(url)
    time.sleep(5)
    container = driver.find_element(By.ID, "main").find_element(By.ID, "main-container")
    item = []
    link =url
    title = container.find_element(By.CLASS_NAME, "product-details-full-content-header").find_element(By.CLASS_NAME, "product-details-full-content-header-title").text
    sku = title.split(" ")[0]
    desc = container.find_element(By.CLASS_NAME, "product-details-full-content-header").find_element(By.CLASS_NAME, "pdp-description").get_attribute('innerHTML')
    desc += "<p></p><p><strong>Customise your order - Request a Quote</strong></p><p>Price online is based on the cost of the item with no branding. Custom branding prices are additional.</p><p>Submit a quote request to receive pricing based on your logo branding needs and quantity you require.</p>"
    images = []
    variants =[]
    price =''

    # image cover
    image_cover=""
    try:
        image_cover = container.find_element(By.CLASS_NAME, "product-details-image-gallery").find_element(By.CLASS_NAME,"bx-viewport").find_elements(By.TAG_NAME,"li")[1].find_element(By.TAG_NAME,"img").get_attribute("src")
    except Exception:
        image_cover = container.find_element(By.CLASS_NAME, "product-details-image-gallery").find_element(By.CLASS_NAME,"product-details-image-gallery-detailed-image").find_element(By.TAG_NAME,"img").get_attribute("src")
    images.append(image_cover)

    # moving across color selection by click
    colors = container.find_element(By.CLASS_NAME, "color-option-container").find_element(By.CLASS_NAME, "color-option-colors-list")
    color = colors.find_elements(By.TAG_NAME, "div")
    for color_ in range(1,len(color)+1):

        colors.find_element(By.CSS_SELECTOR, f"div:nth-of-type({color_})").click()
        color_item = colors.find_element(By.CSS_SELECTOR, f"div:nth-of-type({color_})").find_element(By.TAG_NAME,"span").text
        
       
        # image selections
        try:
            image = container.find_element(By.CLASS_NAME, "product-details-image-gallery").find_element(By.CLASS_NAME, "bx-pager")
            image_links = image.find_elements(By.TAG_NAME, "div")
            for img_ in range(1,len(image_links)+1):
                images.append(image.find_element(By.CSS_SELECTOR, f"div:nth-of-type({img_})").find_element(By.TAG_NAME,"img").get_attribute("src"))
        except Exception:
            images.append(container.find_element(By.CLASS_NAME, "product-details-image-gallery").find_element(By.TAG_NAME,"img").get_attribute("src"))
        size_table = container.find_element(By.CLASS_NAME, "size-option-table")

        size_ = size_table.find_element(By.TAG_NAME, "thead")
        size__ = size_.find_elements(By.TAG_NAME,"td")
        stock= size_table.find_element(By.TAG_NAME, "tbody")
        stock_ = stock.find_elements(By.TAG_NAME,"td")
        for __ in range(2,len(size__)+1):
            variant = []
            tag_size = size_.find_element(By.CSS_SELECTOR, f"td:nth-of-type({__})").text
            if tag_size == " " or tag_size == None:
                tag_size =""
            #print(tag_size)
            tag_stock = stock.find_element(By.CSS_SELECTOR, f"td:nth-of-type({__})").find_element(By.CLASS_NAME,"stock-info").text.split(" ")[0]
            price =stock.find_element(By.CSS_SELECTOR, f"td:nth-of-type({__})").find_element(By.CLASS_NAME, "subitem-price").text
            #print(tag_stock, tag_price)

        #print(title, desc, variants, sku, link,color_item)
            variants.append({'color': color_item, 'size': tag_size, 'stock':tag_stock})
    item.append({'sku': sku, 'link': link, 'title': title, 'lowest_price': price, 'tags': '', 'description': desc, 'product_image': images, 'variants': variants})  
    print(item) 
    return item 

#SHOPIFY
def remove_empty_lists (lst):
    return [ e for e in lst if len(e)!=0]
def modifyPrice(price):
    price = float(price.split("$")[1])
    return str(round(float(price) * 1.6,2))

def createNewProducts(data, colorList, sizeList, type):
    variant = data["variants"][0]
    colorList = [*set(colorList)]
    sizeList = [*set(remove_empty_lists(sizeList))]
    url = f"https://{store}/admin/api/2023-07/products.json"
    price = modifyPrice(data["lowest_price"])
    
    if len(sizeList) != 0 :
        payload = {
            "product": {
                "title": f'{data["title"]}',
                "body_html": data["description"],
                "vendor": "Shiny",
                "product_type": type,
                "status": "draft",
                "published_scope": "web",
                "tags": data["tags"],
                    "variant": { 
                    "title": f'{variant.get("color")} {variant.get("size")}', 
                    "option1": variant.get("color"),
                    "option2": variant.get("size"),
                    "sku":  f'{data["sku"]}.{variant.get("color")}.{variant.get("size")}',
                    "price": price,
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
            "title": f'{data["title"]}',
            "body_html": data["description"],
            "vendor": "Shiny",
            "status": "draft",
            "published_scope": "web",
            "tags": data["tags"],
             "variant": {   
                    "title": variant.get("color"), 
                    "option1": variant.get("color"),
                    "sku": f'{data["sku"]}.{variant.get("color")}',
                    "price": price,
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
            "Accept": "aplication/json"
        }
        response = requests.request("POST", url, json=payload, headers=headers)
def addStockVariant(productId, variantId, variant, product): 
    price = modifyPrice(product["lowest_price"])
  
    url = f'https://{store}/admin/api/2023-07/products/{productId}.json'
    if variant.get('size') != "" and variant.get('size') != " ":
        #Has size
        payload = {
            "product": {
                "variant": {
                    "id": variantId,     
                    "title": f'{variant.get("color")} {variant.get("size")}', 
                    "option1": variant.get("color"),
                    "option2": variant.get("size"),
                    "sku":  f'{product["sku"]}.{variant.get("color")}.{variant.get("size")}',
                    "price": price,
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
                    "price": price,
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

#Adjusts the inventory level of an inventory item at a location
def adjustInventoryLevel(inventoryId, adjust):

    url = f'https://{store}/admin/api/2023-07/inventory_levels/adjust.json'
    payload = {
        "location_id": location,
        "inventory_item_id": inventoryId,
        "available_adjustment": re.sub("[+,]","",adjust),
    }
    headers = {
        "Content-Type": "application/json",
        "X-Shopify-Access-Token": token,
        "Accept": "aplication/json"
    }

    response = requests.request("POST", url, json=payload, headers=headers)
def adjustInventoryPrice(productid, variantid,  price):

    url = f'https://{store}/admin/api/2023-07/products/{productid}.json'
    querystring = {"vendor":"Shiny"}
    payload = {"product": {
            "id": productid,
            "variants":[{
              "id": variantid,
              "price": modifyPrice(price)
        }]
      }
    }
    headers = {
        "Content-Type": "application/json",
        "X-Shopify-Access-Token": token
    }
   
    response = requests.request("PUT", url, json=payload, headers=headers, params=querystring)
    print(f'{productid} -{variantid} -{price}')
    print(json.loads(response.text))
    time.sleep(1)


def addNewStockVariant(productId, variant, product): 
    price = modifyPrice(product["lowest_price"])

    url = f'https://{store}/admin/api/2023-07/products/{productId}/variants.json'
    if variant.get('size') != "" and variant.get('size') != " ":
        payload = {
            "variant": {    
                "sku": f'{product["sku"]}.{variant.get("color")}.{variant.get("size")}',
                "title": f'{variant.get("color")} {variant.get("size")}', 
                "option1": variant.get("color"),
                "option2": variant.get("size"),
                "price": price,
                "inventory_management": "shopify"
            }}
    else:
        payload = {
        "variant": {    
            "sku":f'{product["sku"]}.{variant.get("color")}',
            "title": variant.get("color"),
            "option1": variant.get("color"),
            "price": price,
            "inventory_management": "shopify"
    }}
    headers = {
        "Content-Type": "application/json",
        "X-Shopify-Access-Token": token,
        "Accept": "aplication/json"
    }

    response = requests.request("POST", url, json=payload, headers=headers)
    print(f'>>  response Add new stock variant {response.status_code}')
    if response.status_code == 422:
        variant =''
    else:
        # Send email notification
        #logger.info(f'{product["sku"]}.{variant.get("color")}')
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

def existingProducts():

    url = f"https://{store}/admin/api/2023-07/products.json"
    isNotLimit = True
    lastId = 1 # 8444626239795
    list = []
    #Running through pagination    
    count= 0
    while isNotLimit:
        querystring = {
            "vendor":"Shiny", 
            "limit": 250,
            "since_id": lastId
            }
        headers = {
            "Content-Type": "application/json",
            "X-Shopify-Access-Token": token
        }

        response = requests.request("GET", url, headers=headers, params=querystring)
        products = json.loads(response.text)

        if len(products["products"]) == 0: 
            isNotLimit = False
        else:
            print(f"Total existing products for this batch: %s" % len(products["products"]))
            count=+  len(products["products"])
            lastId = products["products"][-1]["id"]
            for p in products["products"]:
                for v in p["variants"]:
                    list.append(v["sku"])
    print( f'Total product count for Shiny : {str(count)} .')
    return list
def getProductsByTitle(title):
    print(title)
    url = f"https://{store}/admin/api/2023-07/products.json"
    querystring = {"vendor":"Shiny","title":title}
    headers = {
        "Content-Type": "application/json",
        "X-Shopify-Access-Token": token,
        "Accept": "aplication/json"
    }
    response =''
    response = requests.request("GET", url, headers=headers, params=querystring)
    print(response.status_code)
    if response.status_code !=200 & response.status_code !=201: 
        print('exceeded limit call per second for shopify')
        print(response.text)
        time.sleep(5)
        response = requests.request("GET", url, headers=headers, params=querystring)
        time.sleep(2)

    products = json.loads(response.text)
    return products


def createNewProductShiny(product, type):
   
    colorList = [p.get('color') for p in product["variants"]]
    sizeList = [p.get('size') for p in product["variants"]]
    pr = createNewProducts(product, colorList, sizeList,type)
    
    time.sleep(1)
    # Add image
    try:
        addImage(pr["product"]['id'], product["product_image"])
    except Exception:
        print("error creating new product")
    time.sleep(1)
    
    # if product item only have one variant, modify exiting variant
    # if product item has more than one variant, modify the first variant and create new variants for the rest of the list
    print(product["variants"])

    for j in range(len(product["variants"])):
        if j == 0:   
            print(pr)
            vr = addStockVariant(pr['product']['id'], pr["product"]['variants'][0]['id'], product["variants"][j], product)
            time.sleep(1)
            addInventoryLevel(vr["product"]["variants"][0]["inventory_item_id"],product["variants"][j]["stock"])
            time.sleep(1)
        if j > 0:
            try:
                vr = addNewStockVariant(pr["product"]["id"], product["variants"][j], product)
                time.sleep(1)
                print(vr)
                if vr =='':
                    continue
                else:
                    addInventoryLevel(vr["variant"]["inventory_item_id"],product["variants"][j]["stock"])
                time.sleep(1)
            except:
                continue

def processing(driver,winning_spirit_items):

    seen = set()
    new_l = []
    for d in winning_spirit_items:
        t = tuple(d.items())
        if t not in seen:
            seen.add(t)
            new_l.append(d)
    winning_spirit_items = new_l

    print(len(winning_spirit_items))
    for _ in winning_spirit_items:
        print(_)
       

        products = scrapeItem(driver,_['url'], _['cat'] , '', '')
        #Get existing products from LegendLife
        print("***** MODIFICATION *****")
        e_Products= []
        e_Products = existingProducts() # list of sku items
        print(e_Products)

        setSku = []
        for e_Product in e_Products:
            if e_Product.split(".")[0]is not None:
                setSku.append(e_Product.split(".")[0])
        setSku = set(setSku)
        print(setSku)

        for i in range(len(products)):

            # Scanning existing products
            # If existing product, update stock level only
            # if not existing product, create new product

            if products[i]["sku"] not in e_Products:
                if products[i]["sku"] not in setSku:
                    # Create new product
                    print(">> ***[create new product]***")
                    print(products)
                    print(f'{products[i]["sku"]}.{products[i]["title"]}')
                    createNewProductShiny(products[i], _['cat'].split("/")[-1])
                else:
                    # Update existing product stock level 
                    print(f'updating ... {products[i]["sku"]}.{products[i]["title"]}')
                    print(products)
                    p = getProductsByTitle(f'{products[i]["sku"]}.{products[i]["title"]}')
                    time.sleep(2)
                    #By pass error products
                    try:
                        a =p["products"][0]
                        print(a)
                        
                        for v in p["products"][0]["variants"]: #from shopify
                            # Correct price
                            # adjustInventoryPrice(a["id"],v["id"], products[i]["lowest_price"])

                            # variant already exits, add adjustment stock level
                            if len(p["products"][0]["variants"]) == len(products[i]["variants"]):
                                for v_ in products[i]["variants"]: #from legend scraper
                                    if (v["sku"] == f'{products[i]["sku"]}.{v_["color"]}.{v_["size"]}') or (v["sku"] == f'{products[i]["sku"]}.{v_["color"]}'):
                                        if v_["stock"] is None:
                                            v_["stock"] = '0'
                                        adjust = int(re.sub("[+,]","",v_["stock"])) - v["inventory_quantity"]
                                        if adjust != 0:
                                            print(f'** 2nd updating stock level product {products[i]["sku"]} **')
                                            print(f"[Adustment] stock level {adjust}")
                                            print( f"[Adustment] stock level for {v['inventory_item_id']} - adjust {adjust} .")
                                            adjustInventoryLevel(v["inventory_item_id"], str(adjust))
                                            time.sleep(3)
                            
                            # variant not exit, create new variant 'ST9020.Black Opal.S'
                            if len(p["products"][0]["variants"]) < len(products[i]["variants"]):
                                print("[Detect] new variant-- Adding...")
                                vrExiting = [vrl["sku"] for vrl in p["products"][0]["variants"]] # from shopify, sku = sku.color.size
                                vrInNewData = []
                                for v_ in products[i]["variants"]: # from legend scraper
                                    if v_["size"] != "":
                                        print(f'{products[i]["sku"]}.{v_["color"]}.{v_["size"]}')
                                        if f'{products[i]["sku"]}.{v_["color"]}.{v_["size"]}' not in vrExiting:
                                            try:
                                                vr = addNewStockVariant(p["products"][0]["id"], v_, products[i])
                                                time.sleep(1)
                                                print(vr)
                                                if vr =='':
                                                    continue
                                                else:
                                                    addInventoryLevel(vr["variant"]["inventory_item_id"],v_["stock"])
                                                time.sleep(1)
                                            except:
                                                continue
                                    if v_["size"] == "":
                                        print(f'{products[i]["sku"]}.{v_["color"]}')
                                        if f'{products[i]["sku"]}.{v_["color"]}' not in vrExiting:
                                            try:
                                                vr = addNewStockVariant(p["products"][0]["id"],v_, products[i])
                                                time.sleep(1)
                                                print(vr)
                                                if vr =='':
                                                    continue
                                                else:
                                                    addInventoryLevel(vr["variant"]["inventory_item_id"],v_["stock"])
                                                time.sleep(1)
                                            except:
                                                continue
                                
                    except Exception:
                        print(p)
                        print(products[i])
                        pass
## Set Chrome Options

options = webdriver.ChromeOptions()
options.add_argument('ignore-certificate-errors')
options.add_argument("--headless=new")
options.add_argument("--start-maximized")
options.add_argument("--no-sandbox") 
options.add_argument("--disable-dev-shm-usage")
# options.add_experimental_option("excludeSwitches", ["enable-automation"])
# options.add_experimental_option('useAutomationExtension', False)
driver = webdriver.Chrome()
# driver.get(url_)
# time.sleep(10)
driver.get(URL)
time.sleep(5)
# assertIn("search", driver.title)
wait = WebDriverWait(driver, 20)
username = driver.find_element(By.ID, "login-email")
password = driver.find_element(By.ID, "login-password")
username.send_keys(e)
password.send_keys(p)
driver.find_element(By.CLASS_NAME,"login-register-login-submit").click()
time.sleep(3)


# collection/sub/cat/item
# winning spirit
getItemLink(driver, link1,'')
processing(driver,winning_spirit_items)

winning_spirit_subs =[]
winning_spirit_cat_url = []
winning_spirit_items = []
# bench marks
getItemLink(driver, link2,'')
processing(driver,winning_spirit_items)

winning_spirit_subs =[]
winning_spirit_cat_url = []
winning_spirit_items = []
# australian industrial
getItemLink(driver, link3,'')
processing(driver,winning_spirit_items)