import promo_brands
import requests
import json 
import pprint
import base64
import re
from datetime import datetime as dt
import schedule
import time
import logging

import os

client_id = os.environ['CLIENT_ID']
refresh_token = os.environ['REFRESH_TOKEN']
token =os.environ['TOKEN']
store=os.environ['STORE']
location=os.environ['LOCATION']

# function to encode file data to base64 encoded string
def encodeFile(link):
    return base64.b64encode(requests.get(link).content).decode('utf-8')

def addImage(id, links):
    payload = []
    for link in links:
        payload={
            "image": {
                "attachment": encodeFile(list(link)[0])
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
    payload = {
        "product": {
            "variant": {
                "id": variantId,     
                "title": variant.get("color"), 
                "option1": variant.get("color"),
                "sku": variant.get("itemNumber"),
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
    logging.info(f'>> response Add stock variant {response.status_code}')
    variant = json.loads(response.text)
    return variant
def addNewStockVariant(productId, variant, product): 
    url = f'https://{store}/admin/api/2023-07/products/{productId}/variants.json'
    payload = {
        "variant": {    
            "sku": variant.get("itemNumber"),
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
    logging.info(f'>>  response Add new stock variant {response.status_code}')
    if response.status_code == 422:
        # if error because of duplicate title/option1, combine name variant and variant itemNumber
        payload = {
        "variant": {    
            "sku": variant.get("itemNumber"),
            "title": f'{variant.get("color")} {variant.get("itemNumber")}',
            "option1": f'{variant.get("color")} {variant.get("itemNumber")}',
            "price": re.sub("[^\d\.]","",str(product["lowest_price"])),
            "inventory_management": "shopify"
        }}
        response = requests.request("POST", url, json=payload, headers=headers)
    variant = json.loads(response.text)
    return variant

def addInventoryLevel(inventoryId, avail):
    logging.info(f'{str(inventoryId)} - stock level: {avail}')
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

def createNewProducts(data):
    url = f"https://{store}/admin/api/2023-07/products.json"
  
    payload = {
        "product": {
            "title": data["name"],
            "body_html": data["description"],
            "vendor": "Promo Brands",
            "status": "draft",
            "published_scope": "web",
            "tags": data["tags"]
        }}
    headers = {
        "Content-Type": "application/json",
        "X-Shopify-Access-Token": token,
        "Accept": "aplication/json"
    }

    response = requests.request("POST", url, json=payload, headers=headers)
    products = json.loads(response.text)
   
    return products

def getProductsByTitle(title):
    url = f"https://{store}/admin/api/2023-07/products.json"
    querystring = {"vendor":"Promo Brands","title":title}
    headers = {
        "Content-Type": "application/json",
        "X-Shopify-Access-Token": token,
        "Accept": "aplication/json"
    }
    response =''
    response = requests.request("GET", url, headers=headers, params=querystring)
    logging.info(response.status_code)
    if response.status_code !=200 & response.status_code !=201: 
        logging.info('exceeded limit call per second for shopify')
        logging.info(response.text)
        time.sleep(5)
        response = requests.request("GET", url, headers=headers, params=querystring)
        time.sleep(2)

    products = json.loads(response.text)
    return products

def existingProducts():
    url = f"https://{store}/admin/api/2023-07/products.json"
    isNotLimit = True
    lastId = 1 # 8444626239795
    list = []
    #Running through pagination    
    while isNotLimit:
        querystring = {
            "vendor":"Promo Brands", 
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
            logging.info(f"Total existing products for this batch: %s" % len(products["products"]))
            lastId = products["products"][-1]["id"]
            for p in products["products"]:
                for v in p["variants"]:
                    list.append(v["sku"])
    return list


def checkVariantExists(product, e_product):
    check = False
    if len(product["variants"]) == 0:
        logging.info(f'Offshore express {product["product_code"]} {product["name"]}')
        check = True
    else:    
        for v in product["variants"]:
            if v.get("itemNumber") in e_product:
                check = True
                break
    return check
def checkUpdateVariants(product, e_product):
    check = False
    if len(product["variants"]) != 0: 
        for v in product["variants"]:
            if v.get("itemNumber") in e_product:
                check = True
                break
    return check
def process(products, e_Products):
    for i in range(len(products)):

        # Scanning existing products
        # If existing product, update stock level only
        # if not existing product, create new product

        if products[i]["product_code"] not in e_Products:
            if checkVariantExists(products[i], e_Products) is False:
                logging.info(f'Adding PromoBrands {products[i]["product_id"]} -  {products[i]["product_code"]}')
                # Create a new product
                pr = createNewProducts(products[i])
                time.sleep(1)
                logging.info(f'Adding product {pr["product"]["id"]}')
                # Add image
                addImage(pr["product"]['id'], products[i]["product_image"])
                time.sleep(1)
                
                # if product item only have one variant, modify exiting variant
                # if product item has more than one variant, modify the first variant and create new variants for the rest of the list
                logging.info(products[i]["variants"])
            
                for j in range(len(products[i]["variants"])):
                    if j == 0:
                        
                        vr = addStockVariant(pr['product']['id'], pr["product"]['variants'][0]['id'], products[i]["variants"][j], products[i])
                        time.sleep(1)
                        addInventoryLevel(vr["product"]["variants"][0]["inventory_item_id"],products[i]["variants"][j]["stock"])
                        time.sleep(1)
                    if j > 0:
                        logging.info(f'[new variant] {products[i]["variants"][j].get("itemNumber")}' )
                        vr = addNewStockVariant(pr["product"]["id"], products[i]["variants"][j], products[i])
                        time.sleep(1)
                        logging.info(vr)
                        addInventoryLevel(vr["variant"]["inventory_item_id"],products[i]["variants"][j]["stock"])
                        time.sleep(1)
        
        # Update product
        # Case: have more than one variant 
            elif checkUpdateVariants(products[i], e_Products) is True :      
                p = getProductsByTitle(products[i]["name"])
                time.sleep(2)
                #By pass error products
                try:
                    a =p["products"][0]
                    
                    for v in p["products"][0]["variants"]:

                        # variant already exits, add adjustment
                        for v_ in products[i]["variants"]:
                            if v["sku"] == v_["itemNumber"]:
                                if v_["stock"] is None:
                                    v_["stock"] = '0'
                                adjust = int(re.sub("[+,]","",v_["stock"])) - v["inventory_quantity"]
                                if adjust != 0:
                                    logging.info(f'** 2nd updating stock level product {products[i]["product_code"]} **')
                                    logging.info(f"[Adustment] stock level {adjust}")
                                    adjustInventoryLevel(v["inventory_item_id"], str(adjust))
                                    time.sleep(3)
                        # variant not exit, create new variant
                        if len(p["products"][0]["variants"]) < len(products[i]["variants"]):
                            logging.info("[Detect] new variant-- Adding...")
                            vrExiting = [vrl["sku"] for vrl in p["products"][0]["variants"]]
                            vrList = [v for v in products[i]["variants"] if v["itemNumber"] not in vrExiting]
                            logging.info(vrList)
                            for subVr in vrList:
                                vr = addNewStockVariant(p["products"][0]["id"], subVr, products[i])
                                time.sleep(1)
                                logging.info(vr)
                                addInventoryLevel(vr["variant"]["inventory_item_id"],subVr["stock"])
                                time.sleep(1)
                except:
                    logging.info(p)
                    logging.info(products[i]["name"])
                    pass
        # case: 1 variant
        elif products[i]["product_code"] in e_Products:
            if checkUpdateVariants(products[i], e_Products) is True :
                p = getProductsByTitle(products[i]["name"])
                time.sleep(2)
                #By pass error products
                try:
                    a =p["products"][0]

                    for v in p['products'][0]['variants']:
                        # variant already exits, add adjustment
                        for v_ in products[i]["variants"]:

                            if v["sku"] == v_["itemNumber"]:
                                if v_["stock"] is None:
                                    v_["stock"] = '0'
                                adjust = int(re.sub("[+,]","",v_["stock"])) - v["inventory_quantity"]
                                if adjust != 0:
                                    logging.info(f'** 1rd updating stock level product {products[i]["product_code"]} **')
                                    logging.info(f"[Adustment] stock level {adjust}")
                                    adjustInventoryLevel(v["inventory_item_id"], str(adjust))
                                    time.sleep(1)
                except:
                    logging.info(p)
                    logging.info(products[i]["name"])
                    pass

def init():
    start = dt.now()
    e_Products= []
    e_Products = existingProducts() # list of sku items
    logging.info(e_Products)

    products =[]
    token_ = promo_brands.gettoken()
    # Run loop for pagination
    last_product = 19031 #18240 #18344 #18447 #18554 18655 18758 18859 18965 19067 19031 22650 22625

    products = promo_brands.getPromoBrandProducts(token_, last_product)
   
    last_product = products[-1]['product_id']
    logging.info(f'******** Last Product ID {last_product} **********')
    process(products, e_Products)
    
    # IsNotPromoBrandLimit = True
    # while IsNotPromoBrandLimit:
    #     products = promo_brands.getPromoBrandProducts(token_, last_product)

    #     if len(products) == 0:
    #         IsNotPromoBrandLimit = False
    #     else:
    #         last_product = products[-1]['product_id']
    #         logging.info(f'******** Last Product ID {last_product} **********')
    #         process(products, e_Products)

    end = dt.now()
    elapsed = end - start
    logging.info("Total running times: %02d:%02d:%02d:%02d" % (elapsed.days, elapsed.seconds // 3600, elapsed.seconds // 60 % 60, elapsed.seconds % 60))

        
if __name__ == "__main__":
    try:
        logging.basicConfig(filename='logs.log',
                        filemode='a',
                        format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                        datefmt='%m/%d/%Y %I:%M:%S %p',
                        level=logging.INFO)
        logging.info("STARTING")
        # Every day at 6am or 06:00 time init() is called.
        init()
        # schedule.every().day.at("06:00").do(init)
        # while True:
        #     schedule.run_pending()
        #     time.sleep(1)

    except:
        print("STOPPING")
 
    
