import requests
import json 
import re
import time
import base64
import os
import time
import math
import logging 


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO, filename='trend.log')

logger = logging.getLogger(__name__)

def getShopifyProducts(shopURL, token):
    url = f"https://{shopURL}/admin/api/2023-07/products.json"

    querystring = {"vendor":"Custom Branded Merch"}

    headers = {
        "X-Shopify-Access-Token": token,
        "Content-Type": "application/json",
        "Accept": "aplication/json",
        "Authorization": f"Bearer {token}"
    }

    response = requests.request("GET", url, headers=headers, params=querystring)
    print(response.text)

def existingProducts(store, token):
    url = f"https://{store}/admin/api/2023-07/products.json"
    list_ = []

    # get active product
    isNotLimit = True
    lastId = 1 # 8444626239795
    
    #Running through pagination    
    count= 0
    while isNotLimit:
        querystring = {
            "vendor":"Custom Branded Merch", 
            "limit": 250,
            "since_id": lastId,
            "status": "active"
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
            count=  len(products["products"]) +count
            lastId = products["products"][-1]["id"]
            for p in products["products"]:
                list_.append(p)
    print( f'Total ACTIVE product count for Custom Branded Merch : {str(count)}')
    
    # get draft products
    isNotLimit_ = True
    lastId_ = 1 # 8444626239795
    
    #Running through pagination    
    count_= 0
    while isNotLimit_:
        querystring_ = {
            "vendor":"Custom Branded Merch", 
            "limit": 250,
            "since_id": lastId_,
            "status": "draft"
            }
        headers_ = {
            "Content-Type": "application/json",
            "X-Shopify-Access-Token": token
        }

        response_ = requests.request("GET", url, headers=headers_, params=querystring_)
        products_ = json.loads(response_.text)

        if len(products_["products"]) == 0: 
            isNotLimit_ = False
        else:
            print(f"Total existing products for this batch: %s" % len(products_["products"]))
            count_=  len(products_["products"]) +count_
            lastId_ = products_["products"][-1]["id"]
            for p_ in products_["products"]:
                list_.append(p_)              
        print( f'Total DRAFT product count for Custom Branded Merch : {str(count_)}')
    return { "products" : list_}

def encodeFile(link):
    return base64.b64encode(requests.get(link).content).decode('utf-8')

def addImage(id, links):
    print(links)
    payload = []
    for link in links:
        link = "https://"+ link.split("//")[1]
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
        print(response.text)

def TrendStockCheck (product_id):

    url = f"https://au.api.trends.nz/api/v1/stock/{product_id}.json"

    querystring = {"":""}

    headers = {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*",
        "Authorization": f"Basic {trend_token}"
    }

    response = requests.request("GET", url, headers=headers, params=querystring)

    print(response.text)

    if response.status_code != 200:
        logger.info(f'{product_id} not available.')
    else:
        if json.loads(response.text)["data"] == []:
            logger.info(f'{product_id} out of stock.')
        else:
            return json.loads(response.text)

def addNewStockVariant(productId, sku, price, variant_desc): 

    url = f'https://{store}/admin/api/2023-07/products/{productId}/variants.json'
    
    payload = {
        "variant": {    
            "sku": f'{sku}.{variant_desc}',
            "title": f'{sku}.{variant_desc}', 
            "option1": variant_desc,
            "price": price,
            "inventory_management": "shopify",
            "inventory_policy": "deny"
        }}
   
    headers = {
        "Content-Type": "application/json",
        "X-Shopify-Access-Token": token,
        "Accept": "aplication/json"
    }

    response = requests.request("POST", url, json=payload, headers=headers)
    print(f'>>  response Add new stock variant {response.status_code} {response.text}')
    if response.status_code == 422:
        variant =''
    else:
        # Send email notification
        #logger.info(f'{product["sku"]}.{variant.get("color")}')
        variant = json.loads(response.text)
    return variant

def addInventoryLevel(inventoryId, avail):
    print(f'{str(inventoryId)} - stock level: {avail}')
   
    url = f'https://{store}/admin/api/2023-07/inventory_levels/set.json'
    payload = {
        "location_id": location,
        "inventory_item_id": inventoryId,
        "available": avail,
    }
    headers = {
        "Content-Type": "application/json",
        "X-Shopify-Access-Token": token,
        "Accept": "aplication/json"
    }

    response = requests.request("POST", url, json=payload, headers=headers)

def UpdateVariant(productId, variantId, variant_desc, sku): 
  
    url = f'https://{store}/admin/api/2023-07/products/{productId}.json'
    payload = {
        "product": {
            "variant": {
                "id": variantId,
                "sku":f'{sku}-{variant_desc}',     
                "title": f'{sku}-{variant_desc}', 
                "option1": variant_desc,
                "inventory_management": "shopify",
                "inventory_policy": "continue"
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

def ArchiveProduct(productId): 
  
    url = f'https://{store}/admin/api/2023-07/products/{productId}.json'
    payload = {
        "product": {
            "status": "archived"
        }
    }
  
    headers = {
        "Content-Type": "application/json",
        "X-Shopify-Access-Token": token,
        "Accept": "aplication/json"
    }

    response = requests.request("PUT", url, json=payload, headers=headers)
    print(f'>> response archiving product {response.status_code}')

#Adjusts the inventory level of an inventory item at a location
def adjustInventoryLevel(inventoryId, adjust):

    url = f'https://{store}/admin/api/2023-07/inventory_levels/adjust.json'
    payload = {
        "location_id": location,
        "inventory_item_id": inventoryId,
        "available_adjustment": adjust,
    }
    headers = {
        "Content-Type": "application/json",
        "X-Shopify-Access-Token": token,
        "Accept": "aplication/json"
    }

    response = requests.request("POST", url, json=payload, headers=headers)
    print(response.status_code)

def UpdatePolicy(productId, variantIds_): 
    print(f'numbr of variants {len(variantIds_)} - product Id {productId}')
    url = f'https://{store}/admin/api/2023-07/products/{productId}.json'

    variants =[]
    for t in range(len(variantIds_)):
        variants.append({
            "id": variantIds_[t]["id"],
            "inventory_policy": "deny"})
  
    payload = {
        "product": {
            "variants": variants
        }
    }
  
    headers = {
        "Content-Type": "application/json",
        "X-Shopify-Access-Token": token,
        "Accept": "aplication/json"
    }

    response = requests.request("PUT", url, json=payload, headers=headers)
    print(f'>> response modify policy {response.status_code}')

def getTrendProductList(page):
    #page = 1
    url = f"https://au.api.trends.nz/api/v1/products.json?inc_discontinued=false&inc_inactive=0&page_no={page}"

    payload = ""
    headers = {
        "User-Agent": "insomnia/8.5.1",
        "Authorization": f"Basic {trend_token}"
    }
    response = requests.request("GET", url, data=payload, headers=headers)
    # print(response.text)
    return json.loads(response.text)


def createTrendNewProduct(trend):
    code = trend["code"]
    name =trend["name"] 
    #-----------------DESC---------
    description = "<p>" +trend["description"] +".</p>"
    # table desc
    specification = ""
    if len(trend["additional_specifications"]) != 0 :
        specification += "<p><strong>Specifications</strong></p><table><thead><tr><td><strong>Name</strong></td><td><strong>Description</strong></td></tr></thead><tbody>"
        for spc in trend["additional_specifications"]:
            specification += "<tr><td>"+spc["specification"] +"</td><td>"+ spc["description"] +"</td></tr>"
        specification += "</tbody></table><p>&nbsp;</p>"    
    
    material =""
    if len(trend["additional_materials"]) != 0:
        material += "<p><strong>Materials</strong></p><table><thead><tr><td><strong>Name</strong></td><td><strong>Description</strong></td></tr></thead><tbody>"
        for m in trend["additional_materials"]:
            material += "<tr><td>"+m["component"] + "</td><td>" +m["material"] +"</td></tr>"
        material += "</tbody></table><p>&nbsp;</p>"

    colors =""
    if trend["colours"] != "":
        colors = "<p><strong>Colors : </strong>"+trend["colours"] +".</p>"
    
    dimension =""
    if len(trend["dimensions"]) != 0:
        dimension = "<p><strong>Dimensions : </strong> " +trend["dimensions"][0] +".</p>"
    
    branding =""
    if len(trend["branding_options"]) != 0:
        for b in trend["branding_options"]:
            branding += "<p><strong>"+b["print_type"] + " :</strong> "+b["print_description"] +"</p>"
    extra__ = "<p><strong>CUSTOMISE YOUR ORDER - REQUEST A QUOTE</strong></p>"
    extra = "<p>Submit a quote request to receive pricing based on your logo branding and quantity you require.</p>"
    extra_ ="<p>Price online is based on the most cost effective branding and order quantity, bulk discounts apply to this product.<br></p>"
    description +=specification+material+colors+dimension+branding+extra__+extra+extra_

    #----------------Pricing-------------------------------
    unit_price = float(trend["pricing"]["prices"][0]["price"])
    branded_price = float(trend["pricing"]["additional_costs"][0]["unit_price"])
    quant_unit = float(trend["pricing"]["prices"][0]["quantity"])
    set_price = float(trend["pricing"]["additional_costs"][0]["setup_price"])
    shipping_price = 40
    price = str(round( ((((unit_price +branded_price)*quant_unit) +set_price+shipping_price)/quant_unit) * 2, 2))
    #price = str(round( unit_price * 2.8, 2))
    

    #----------------IMG---------
    images = []
    if len(trend["images"]) != 0:
        for im in trend["images"]:
            print(im["link"])
            images.append(im["link"])
        
    #----------------VARIANTS--------
    variants = []
    vr =""
    try:
        vr = TrendStockCheck(code)
        for v in vr["data"]:
            variants.append({'color': v["description"], 'stock': v["quantity"] })
        return {
        "title" :name,
        "description": description,
        'sku': code, 
        'lowest_price': price, 
        'tags': '', 
        'product_image': images, 
        'variants': variants
    } 
    except Exception:
        print('>>>---------Error getting variant - no available data------------')


def createNewProducts(data):
    print(data)
    colorList = []
    variants =[]
    if len(data["variants"]) != 0:
        for vr in data["variants"]:
            colorList.append(vr["color"])
            variant = {   
                    "title": vr["color"], 
                    "option1": vr["color"],
                    "sku": f'{data["sku"]}-{data["title"]}.{vr["color"]}',
                    "price": data["lowest_price"],
                    "inventory_management": "shopify",
                    "inventory_policy": "deny"
            } 
            variants.append(variant)
    else:
        print("Error creating new product")
    
    
    url = f"https://{store}/admin/api/2023-07/products.json"
    payload = {
    "product": {
        "title": f'{data["title"]}',
        "body_html": data["description"],
        "vendor": "Custom Branded Merch",
        "status": "draft",
        "published_scope": "web",
        "tags": data["tags"],
        "variants": variants,
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
    

#--------- START --------------------------
#==========================================

# Filter existing products on shopify which is active only
list_existing_products = existingProducts(store, token)
print(len(list_existing_products["products"]))
list_existing_sku = []

# Going through and add to list sku
for prod in list_existing_products["products"]:
    list_existing_sku.append(prod["variants"][0]["sku"].split("-")[0].split(".")[0])

print(list_existing_sku)
logger.info(f'{list_existing_sku}')
logger.info(f'{list_existing_products}')
print(f'list of existing sku on shopify {len(list_existing_sku)}')

# Get product from trend
page = 1
max_page =False
while max_page == False:
    trend_products = getTrendProductList(page)

    print(f'Trend products number {len(trend_products["data"])}')
    if len(trend_products["data"]) == 0:
        max_page = True
        break
    else:
        page += 1
        for trend in trend_products["data"]:

            print(f'>> checking on shopify {trend["code"]}......')
            # check if product is already available
            if str(trend["code"]) not in list_existing_sku:
                print(f'sku {trend["code"]} not exist-----')
                
                # create new product
                processed_product = createTrendNewProduct(trend)
                
                # Filter out products have no data
                if (processed_product is not None ):
                    print(f'....CREATE NEW PRODUCT {trend["code"]} ')     
                    # create sku with format: code-name.variantdesc
                    processed_sku = f'{processed_product["sku"]}-{processed_product["title"]}'
                    new_product = createNewProducts(processed_product)
                    
                    # Add image
                    try:
                        addImage(new_product["product"]['id'], processed_product["product_image"])
                    except Exception:
                        print("error creating image")
                    time.sleep(1)

                    # Add variant
                    for j in range(len(new_product["product"]["variants"])):
                        try:
                            addInventoryLevel(new_product["product"]["variants"][j]["inventory_item_id"],processed_product["variants"][j]["stock"])
                            time.sleep(1)
                        except Exception:
                            continue
            else:
                print(f'>> Stock on sku {trend["code"]} already live')
        

# Check existing products if is out
for p in list_existing_products['products']:
    product_id = p['id']

    # apparently prices are the same for all variants
    price = p['variants'][0]['price']

    # product_id = 7444305248408
    # price = "14.00"
    # first_variant_id = 42206705057944
    # first_inventory_item_id = 44303183151256
    # first_quantity_variant = 0
    # sku = "121795-anvil-6-panel-cap"
    # trend_id = sku.split("-")[0]


    sku = p['variants'][0]['sku']
    trend_id = p['variants'][0]['sku'].split("-")[0]

    try:
        # UpdatePolicy(product_id, p['variants'])
        stocks = TrendStockCheck(trend_id)
        if stocks is None or len(stocks["data"]) == 0:
            # archive product
            print(f"Archive product {sku}")
            ArchiveProduct(product_id)

        else:
            print(f'number of variant {len(stocks["data"])}')
            # update variant stock level

            for i in range(len(stocks["data"])):
                desc_1 = stocks["data"][i]["description"]
                stock_1 =stocks["data"][i]["quantity"]
                try:
                    # checking if it is missing variant, otherwise adjust stock level
                    variant_id = p['variants'][i]["id"]
                    inventory_item_id = p['variants'][i]["inventory_item_id"]
                    quantity_variant = p['variants'][i]["inventory_quantity"]

                    print(f' {desc_1} , {stock_1} adjusting ...')
                    adjustInventoryLevel(inventory_item_id, stocks["data"][i]["quantity"] - quantity_variant)

                    # if i == 0:
                    #     fix first variant with quantity & add option1
                    #     UpdateVariant(product_id, first_variant_id,  stocks["data"][i]["description"], sku)
                    #     time.sleep(1)
                
                except Exception: 
                    # create another variant as look like it is missing     
                    try:
                        vr = addNewStockVariant(product_id, sku, price, desc_1)
                        time.sleep(1)
                        print(vr)
                        if vr =='':
                            continue
                        else:
                            addInventoryLevel(vr["variant"]["inventory_item_id"],stock_1)
                        time.sleep(1)
                    except:
                        continue
    except Exception:
        print("error")


