import promo_brands
import requests
import json 
import pprint
import base64
import re
from datetime import datetime as dt
from datetime import date
import schedule
import time
import logging
import logging.handlers
import os

from http.server import BaseHTTPRequestHandler, HTTPServer
import threading



hostName = "localhost"
serverPort = 8080

class MyServer(BaseHTTPRequestHandler):
  def do_GET(self):
    self.send_response(200)
    self.send_header("content-Type", "text/html")
    self.end_headers()

client_id = os.environ['CLIENT_ID']
refresh_token = os.environ['REFRESH_TOKEN']
token =os.environ['TOKEN']
store=os.environ['STORE']
location=os.environ['LOCATION']
fromemail= os.environ['FROM']
toemail=os.environ['TO']
password=os.environ['PASSWORD']

message=""

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO, filename='log.log')

logger = logging.getLogger(__name__)

smtp_handler = logging.handlers.SMTPHandler(mailhost=('smtp.gmail.com', 587),
                                        fromaddr=fromemail,
                                        toaddrs=[toemail,fromemail],
                                        subject='CustomBrands Shopify Updates',
                                        credentials=(
                                            fromemail,
                                            password),
                                        secure=())
logger.addHandler(smtp_handler)

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
    print(f'>> response Add stock variant {response.status_code}')
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
    print(f'>>  response Add new stock variant {response.status_code}')
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
    #time.sleep(1)
    response = requests.request("GET", url, headers=headers, params=querystring)
    print(response.status_code)
    if response.status_code !=200 & response.status_code !=201: 
        print('exceeded limit call per second for shopify')
        print(response.text)
        # time.sleep(5)
        response = requests.request("GET", url, headers=headers, params=querystring)
        time.sleep(2)

    products = json.loads(response.text)
    time.sleep(1)
    return products

def existingProducts():
    global message 
    url = f"https://{store}/admin/api/2023-07/products.json"
    isNotLimit = True
    lastId = 1 # 8444626239795
    list = []
    #Running through pagination    
    count= 0
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
            print(f"Total existing products for this batch: %s" % len(products["products"]))
            count= count+ int(len(products["products"]))
            lastId = products["products"][-1]["id"]
            for p in products["products"]:
                for v in p["variants"]:
                    list.append(v["sku"])
    message+= f'Total product count for Promobrands : {str(count)} .'
    return list


def checkVariantExists(product, e_product):
    check = False
    if len(product["variants"]) == 0:
        print(f'Offshore express {product["product_code"]} {product["name"]}')
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
    global message
    for i in range(len(products)):

        # Scanning existing products
        # If existing product, update stock level only
        # if not existing product, create new product

        if products[i]["product_code"] not in e_Products:
            if checkVariantExists(products[i], e_Products) is False:
                print(f'Adding PromoBrands {products[i]["product_id"]} -  {products[i]["product_code"]}')
                message += f'Adding PromoBrands sku {products[i]["product_code"]} {products[i]["name"]}'
                # Create a new product
                pr = createNewProducts(products[i])
                time.sleep(1)
                print(f'Adding product {pr["product"]["id"]}')
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
                        print(f'[new variant] {products[i]["variants"][j].get("itemNumber")}' )
                        vr = addNewStockVariant(pr["product"]["id"], products[i]["variants"][j], products[i])
                        time.sleep(1)
                        print(vr)
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
                              if v["sku"] == v_["itemNumber"]:
                                  l= ""
                                  print(f'** Detect 2nd updating {v_["stock"]} ... {v["inventory_quantity"]} **')
                                  if v_["stock"] is None:
                                      v_["stock"] = '0'
                                  if v_["stock"] == '0':
                                      l = "[OUT OF STOCK] this item is out of stock"
                                      print("out of stock")
                                      print(l)
                                      #message += f"[Adustment] stock level for {v['sku']} {l}"
                                  adjust=""
                                  try: 
                                      adjust = int(re.sub("[+,]","",v_["stock"])) - v["inventory_quantity"]
                                  except:
                                      adjust = 0  
                                      print(f"[Adustment] stock level for {v['sku']} - adjust {adjust} {l}.")
                                      #message += f"[Adustment] stock level for {v['sku']} - adjust {adjust}."
                                  if adjust != 0 and adjust != "":
                                      print(f'** 2nd updating stock level product {products[i]["product_code"]} ** {l}')
                                      print(f"[Adustment] stock level {adjust}")
                                      message += f" [Adustment] stock level for {v['sku']} - adjust {adjust}."
                                      adjustInventoryLevel(v["inventory_item_id"], str(adjust))
                                      time.sleep(1)
                        # variant not exit, create new variant
                        if len(p["products"][0]["variants"]) < len(products[i]["variants"]):
                            print("[Detect] new variant-- Adding...")
                            message+= "[Detect] new variant-- Adding..."
                            vrExiting = [vrl["sku"] for vrl in p["products"][0]["variants"]]
                            vrList = [v for v in products[i]["variants"] if v["itemNumber"] not in vrExiting]
                            print(vrList)
                            for subVr in vrList:
                                vr = addNewStockVariant(p["products"][0]["id"], subVr, products[i])
                                time.sleep(1)
                                print(vr)
                                message+= f'New stock sku {str(vr["variant"]["sku"])} - {subVr["stock"]} .'
                                addInventoryLevel(vr["variant"]["inventory_item_id"],subVr["stock"])
                                time.sleep(1)
                except:
                    print(p)
                    print(products[i]["name"])
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
                                l = ""     
                                print(f'** Detect 1st updating {v_["stock"]} ... {v["inventory_quantity"]} **')
                                if v_["stock"] is None:
                                    v_["stock"] = '0'
                                if v_["stock"] == '0':
                                    l = "[OUT OF STOCK] this item is out of stock"
                                    print("out of stock")
                                    time.sleep(1)
                                    #message += f"[Adustment] stock level for {v['sku']} {l}"
                                adjust =""
                                try: 
                                    adjust = int(re.sub("[+,]","",v_["stock"])) - v["inventory_quantity"]
                                except:
                                    adjust = 0  
                                    print(f"[Adustment] stock level for {v['sku']} - adjust {adjust} {l}.")
                                    #message += f"[Adustment] stock level for {v['sku']} - adjust {adjust} {l}."
                                #adjust = int(re.sub("[+,]","",v_["stock"])) - v["inventory_quantity"]
                                if adjust != 0 and adjust != "":
                                    print(f'** 1st updating stock level product {products[i]["product_code"]} **')
                                    print(f"[Adustment] stock level {adjust}")
                                    message+= f' [Adustment] stock level sku {products[i]["product_code"]} - adjust {adjust} .'
                                    adjustInventoryLevel(v["inventory_item_id"], str(adjust))
                                    time.sleep(1)
                except:
                    print(p)
                    print(products[i]["name"])
                    pass


def init():
    global message
    message = ""
    message += f"Hi Alex, Today's date is {date.today()}"
    start = dt.now()
    e_Products= []
    e_Products = existingProducts() # list of sku items
    print(e_Products)

    products =[]
    token_ = promo_brands.gettoken()
    # Run loop for pagination
    last_product = 1 #18240 #18344 #18447 #18554 18655 18758 18859 18965 19067 19031 22650 22625

#     products = promo_brands.getPromoBrandProducts(token_, last_product)
   
#     last_product = products[-1]['product_id']
#     print(f'******** Last Product ID {last_product} **********')
#     process(products, e_Products)
    
    IsNotPromoBrandLimit = True
    while IsNotPromoBrandLimit:
        products = promo_brands.getPromoBrandProducts(token_, last_product)

        if len(products) == 0:
            IsNotPromoBrandLimit = False
        else:
            last_product = products[-1]['product_id']
            print(f'******** Last Product ID {last_product} **********')
            process(products, e_Products)

    end = dt.now()
    elapsed = end - start
    print("Total running times: %02d:%02d:%02d:%02d" % (elapsed.days, elapsed.seconds // 3600, elapsed.seconds // 60 % 60, elapsed.seconds % 60))
    message +="Total running times: %02d:%02d:%02d:%02d" % (elapsed.days, elapsed.seconds // 3600, elapsed.seconds // 60 % 60, elapsed.seconds % 60) 
    logger.info(message)

def run():
    webServer = HTTPServer((hostName, serverPort), MyServer)
    print("Server started http://%s:%s" % (hostName, serverPort))
    try: 
      webServer.serve_forever()
    except KeyboardInterrupt:
      pass
    webServer.server_close()
    print("Server stopped.")
    
polTime = 1
def scheduleInit():
    while True:
      try:
        init()
      except:
        print("stopping")
      # running once a day
      time.sleep(24* (60*60))
    
   
if __name__ == "__main__":
         
      try:
          print("STARTING")
        # Every day at 6am or 06:00 time init() is called.
        
#         d = threading.Thread(target=scheduleInit, name="Deamon")
#         d.setDaemon(True)
#         d.start()
        
#         # runs the HTTP server
#         run()
          init()
          schedule.every().day.at("06:00").do(init)
        
          while True:
              schedule.run_pending()
              time.sleep(1)
      except:
          print("STOPPING")
     
      
      
 
    
    
