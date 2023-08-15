# Using Selenium WebDriver 2

from bs4 import BeautifulSoup as bs
import requests
import json 
import re
import time
# import logging
# import logging.handlers
import base64
import os

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.chrome.options import Options as ChromeOptions

# token =os.environ['TOKEN']
# store=os.environ['STORE']
# location=os.environ['LOCATION']



# legendlife_email =os.environ['LEGENDLIFE_EMAIL']
# legendlife_pass = os.environ['LEGENDLIFE_PASS']
# legendlife_url = os.environ['LEGENDLIFE_URL']

def getCollectionLink(driver, page):
    # page = 3
    dic = []
    # while page <11:
    driver.get(f"https://www.legendlife.com.au/product_search?limit=100&p={page}")
    products = driver.find_element(By.CLASS_NAME, "products-grid")
    itm = products.find_elements(By.TAG_NAME, 'li')
    print(len(itm))
    for i in range(1,len(itm)+1):
        pag = {}
        product = products.find_element(By.CSS_SELECTOR, f"li:nth-of-type({i})").find_element(By.CLASS_NAME, "product-info")
        link = product.find_element(By.CLASS_NAME, "product-code" ).find_element(By.TAG_NAME, 'a').get_attribute("href")
        title = product.find_element(By.CLASS_NAME, "product-title" ).text
        sku = product.find_element(By.CLASS_NAME, "product-code" ).find_element(By.TAG_NAME, 'a').text
        price = products.find_element(By.CSS_SELECTOR, f"li:nth-of-type({i})").find_element(By.CLASS_NAME, "price-box").find_element(By.CLASS_NAME, "regular-price").find_element(By.CLASS_NAME, "price").text
        price = re.sub("[^\d\.]","",str(price))
        price = str(round(float(price) * 2.5,1))
        pag["sku"] = sku
        pag["link"] = link
        pag["title"] = title
        pag["lowest_price"] = price
        pag["tags"] = "new"
        print(pag)
        dic.append(pag)
    print(dic)
    return dic  


def getData(url, driver):

    driver.find_element(By.ID,"colour-selector-dropdown").click()
    dropdown = Select(driver.find_element(By.ID,"attribute137"))
    fulldata = []
    for i in range(1,len(dropdown.options)):

        dropdown.select_by_value(dropdown.options[i].get_attribute("value"))
        time.sleep(5)
       
       
        try:
            element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "order-summary-row-table-id")))   
            element1 = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "order-summary-row-table-item-qty-class")))
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
        except TimeoutException:
            print("Time exceeded!")
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
    variant = data["variants"][0]
    colorList = [*set(colorList)]
    sizeList = [*set(remove_empty_lists(sizeList))]
    url = f"https://{store}/admin/api/2023-07/products.json"
    price = float(data["lowest_price"])
    
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
            "title": f'{data["sku"]}.{data["title"]}',
            "body_html": data["description"],
            "vendor": "Legend Life",
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
            "Accept": "aaplication/json"
        }
        response = requests.request("POST", url, json=payload, headers=headers)
def addStockVariant(productId, variantId, variant, product): 
    price = float(product["lowest_price"])
  
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
    querystring = {"vendor":"Legend Life"}
    payload = {"product": {
            "id": productid,
            "variants":[{
              "id": variantid,
              "price": float(price)
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
    price = float(product["lowest_price"])

    url = f'https://{store}/admin/api/2023-07/products/{productId}/variants.json'
    if variant.get('size') != "":
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
            "vendor":"Legend Life", 
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
    print( f'Total product count for Legend Life : {str(count)} .')
    return list
def getProductsByTitle(title):
    print(title)
    url = f"https://{store}/admin/api/2023-07/products.json"
    querystring = {"vendor":"Legend Life","title":title}
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


def scrapeLegendLife(driver, page):
    print("***** START SCRAPING *******")
    items = getCollectionLink(driver, page)
    for item in items:
   
        driver.get(item.get("link"))
        
        shortDescription =""
        productSpec =""
        colorSpecs =""
        colorChart =""
        marketSheet =""
        imagePack =""
        warranty =""

        desc = driver.find_element(By.ID, "product_tabs_summary_contents" )
        # short description
        try: 
            shortDescription = f"<p>{desc.find_element(By.CLASS_NAME, 'short-description').text}</p>"
        except NoSuchElementException:
            print("")
        # Product specification
        try:
            productSpecText = desc.find_element(By.XPATH,'//h4[contains(text(),"Product Specifications")]').find_element(By.XPATH, 'following-sibling::*[1]').get_attribute('innerHTML')
            productSpec =f"<h4>Product Specifications</h4>{productSpecText}"
        except NoSuchElementException:
            print("")

        # Color
        try:
            colorText = desc.find_element(By.XPATH,'//h4[contains(text(),"Colours")]').find_element(By.XPATH, 'following-sibling::*[1]').text
            colorSpecs = f"<h4>Colours</h4><p>{colorText}</p>"
        except NoSuchElementException:
            print("")
        # PMS Color chart
        try:
            desc.find_element(By.XPATH,"//h4[contains(text(),'PMS Colour Chart')]")
            colorChartText= desc.find_element(By.XPATH,"//h4[contains(text(),'PMS Colour Chart')]").find_element(By.XPATH, "following-sibling::*[1]").text
            link_ = desc.find_element(By.XPATH,"//h4[contains(text(),'PMS Colour Chart')]").find_element(By.XPATH, "following-sibling::*[1]").find_element(By.TAG_NAME,"a").get_attribute('href')
            colorChart = f"<h4>PMS Colour Chart</h4><ul><li><a href='{link_}' target='_blank' >{colorChartText}</a></li></ul>"
        except NoSuchElementException:
            print("")

        # Marketing info sheet
        try:
            marketSheetText= desc.find_element(By.XPATH,"//h4[contains(text(),'Marketing Info Sheet')]").find_element(By.XPATH, "following-sibling::*[1]").text
            linkSheet = desc.find_element(By.XPATH,"//h4[contains(text(),'Marketing Info Sheet')]").find_element(By.XPATH, "following-sibling::*[1]").find_element(By.TAG_NAME,"a").get_attribute('href')
            marketSheet = f"<h4>Marketing Info Sheet</h4><ul><li><a href='{linkSheet }' target='_blank' >{marketSheetText}</a></li></ul>"
        except NoSuchElementException:
            print("")
        
        # Image Pack
        # try:
        #     imagePackText= desc.find_element(By.XPATH,"//h4[contains(text(),'Image Pack')]").find_element(By.XPATH, "following-sibling::*[1]").text
        #     linkImagePack = desc.find_element(By.XPATH,"//h4[contains(text(),'Image Pack')]").find_element(By.XPATH, "following-sibling::*[1]").find_element(By.TAG_NAME,"a").get_attribute('href')
        #     if imagePackText !="":
        #         imagePack = f"<h4>Image Pack</h4><ul><li><a href='{linkImagePack}' target='_blank' >{imagePackText}</a></li></ul>"
        # except NoSuchElementException:
        #     print("")

        # Warranty
        try:
            w =""
            for e in desc.find_element(By.XPATH,"//h4[contains(text(),'Warranty & Technologies')]").find_element(By.XPATH, "following-sibling::*[1]").find_elements(By.TAG_NAME,"li"):
                warrantyText = e.text
                linkWarranty = e.find_element(By.TAG_NAME,"a").get_attribute('href')
                w += f"<li><a href='{linkWarranty}' target='_blank' >{warrantyText}</a></li>"
            warranty = f"<h4>Warranty & Technologies</h4><ul>{w}</ul>"
        except NoSuchElementException:
            print("")
        customize ="<h4>Customise your order - Request a Quote</h4><p>Submit a quote request to receive pricing based on your logo branding and quantity you require. Bulk discounts apply.</p>"
        item["description"] = shortDescription +  customize + productSpec + colorSpecs + colorChart +marketSheet + warranty
        
        images = driver.find_element(By.CLASS_NAME, "swatchesContainer" ).find_elements(By.TAG_NAME,"a") 
        img_cover = driver.find_element(By.CLASS_NAME, "product-image-zoom" ).find_element(By.TAG_NAME,"a").find_element(By.TAG_NAME,"img").get_attribute('src')
        item["product_image"] = [img_cover] + [image.get_attribute('href') for image in images]
        
        variant = getData(item.get("link"), driver)
        item["variants"] = variant
        
        
    print(items)
    return items

def createNewProductLegendLife(product):
   
    colorList = [p.get('color') for p in product["variants"]]
    sizeList = [p.get('size') for p in product["variants"]]
    pr = createNewProducts(product, colorList, sizeList)
    
    time.sleep(1)
    # Add image
    addImage(pr["product"]['id'], product["product_image"])
    time.sleep(1)
    
    # if product item only have one variant, modify exiting variant
    # if product item has more than one variant, modify the first variant and create new variants for the rest of the list
    print(product["variants"])

    for j in range(len(product["variants"])):
        if j == 0:   
            vr = addStockVariant(pr['product']['id'], pr["product"]['variants'][0]['id'], product["variants"][j], product)
            time.sleep(1)
            addInventoryLevel(vr["product"]["variants"][0]["inventory_item_id"],product["variants"][j]["stock"])
            time.sleep(1)
        if j > 0:
            try:
                vr = addNewStockVariant(pr["product"]["id"], product["variants"][j], product)
                time.sleep(1)
                print(vr)
                addInventoryLevel(vr["variant"]["inventory_item_id"],product["variants"][j]["stock"])
                time.sleep(1)
            except:
                continue

# Enable logging
# logging.basicConfig(
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
#     level=logging.INFO, filename='log.log')

# logger = logging.getLogger(__name__)

# smtp_handler = logging.handlers.SMTPHandler(mailhost=('smtp.gmail.com', 587),
#                                         fromaddr=fromemail,
#                                         toaddrs=[toemail],
#                                         subject='CustomBrands Shopify Updates',
#                                         credentials=(
#                                             fromemail,
#                                             password),
#                                         secure=())
# logger.addHandler(smtp_handler)

def execution():
    print("***** LEGENDLIFE ***********")
    
    e =os.environ['LEGENDLIFE_EMAIL']
    p = os.environ['LEGENDLIFE_PASS']
    URL = os.environ['LEGENDLIFE_URL']     

    #Remote WebDriver
    #firefox_options = webdriver.FirefoxOptions()
    # url = "https://ondemand.us-west-1.saucelabs.com:443/wd/hub"
    # driver = webdriver.Remote(command_executor=url, options=options)
    
    # Get the latest version every day on 1st excution of your program
    driver = webdriver.Firefox()        
    driver.get(URL)
    # assertIn("search", driver.title)
    wait = WebDriverWait(driver, 20)
    username = driver.find_element(By.ID, "email")
    password = driver.find_element(By.ID, "pass")
    username.send_keys(e)
    password.send_keys(p)
    driver.find_element(By.ID,"send2").click()
    page =1
    while page <11:
        print(f'*** Page {page} ***')
        products = scrapeLegendLife(driver, page)
        page += 1

        #products= [{'sku': 'ST9020', 'link': 'https://www.legendlife.com.au/men-s-morgan-crew-neck.html', 'title': "Men's Morgan Crew Neck", 'lowest_price': '26.5', 'tags': 'new', 'description': "<p>Fitted T-shirt for men features collar with rib binding and made of durable single jersey cotton.</p><h4>Customise your order - Request a Quote</h4><p>Submit a quote request to receive pricing based on your logo branding and quantity you require. Bulk discounts apply.</p><h4>Product Specifications</h4>\n<li>Fabric: 100% ring-spun cotton; single jersey</li>\n<ul>\n<li>(GYH: 85% cotton, 15% viscose)</li>\n</ul>\n<li>Weight: 160 g/m²</li>\n<li>Fit: Body Fit</li>\n<li>Sizes: S-2XL</li>\n<li>Care Instructions: washable at 40°C</li>\n<li>Other Features: collar with rib binding, side seams, small size label in the collar, care label in the side seam</li>\n<h4>Colours</h4><p>Black Opal, Crimson Red, Deep Lilac, Daisy Yellow, Green Flash, Grey Heather, King Blue, Military Green, Slate Grey, White, Marine Blue</p><h4>PMS Colour Chart</h4><ul><li><a href='https://www.legendlife.com.au/media/EPI_MediaFolder/ST9020/PMS%20Colour%20Chart/Stedman-Colour-Codes.pdf' target='_blank' >Stedman-Colour-Codes.pdf</a></li></ul><h4>Marketing Info Sheet</h4><ul><li><a href='https://www.legendlife.com.au/media/EPI_MediaFolder/ST9020/Marketing%20Info%20Sheet/ST9020_Marketing%20Info%20Sheet.pdf' target='_blank' >ST9020_Marketing Info Sheet.pdf</a></li></ul>", 'product_image': ['https://www.legendlife.com.au/media/catalog/product/cache/1/image/438x438/9df78eab33525d08d6e5fb8d27136e95/S/T/ST9020_-_Image_3.jpg', 'https://www.legendlife.com.au/media/catalog/product/cache/1/image/9df78eab33525d08d6e5fb8d27136e95/S/T/ST9020-BLO-2XL_-_Image_3.jpg', 'https://www.legendlife.com.au/media/catalog/product/cache/1/image/9df78eab33525d08d6e5fb8d27136e95/S/T/ST9020-CSR-L_-_Image_3.jpg', 'https://www.legendlife.com.au/media/catalog/product/cache/1/image/9df78eab33525d08d6e5fb8d27136e95/S/T/ST9020-DYY-L_-_Image_3.jpg', 'https://www.legendlife.com.au/media/catalog/product/cache/1/image/9df78eab33525d08d6e5fb8d27136e95/S/T/ST9020-DLC-L_-_Image_3.jpg', 'https://www.legendlife.com.au/media/catalog/product/cache/1/image/9df78eab33525d08d6e5fb8d27136e95/S/T/ST9020-GFL-L_-_Image_3.jpg', 'https://www.legendlife.com.au/media/catalog/product/cache/1/image/9df78eab33525d08d6e5fb8d27136e95/S/T/ST9020-GYH-L_-_Image_3.jpg', 'https://www.legendlife.com.au/media/catalog/product/cache/1/image/9df78eab33525d08d6e5fb8d27136e95/S/T/ST9020-KIB-L_-_Image_3.jpg', 'https://www.legendlife.com.au/media/catalog/product/cache/1/image/9df78eab33525d08d6e5fb8d27136e95/S/T/ST9020-MRBLU-L_-_Image_3.jpg', 'https://www.legendlife.com.au/media/catalog/product/cache/1/image/9df78eab33525d08d6e5fb8d27136e95/S/T/ST9020-MIL-L_-_Image_3.jpg', 'https://www.legendlife.com.au/media/catalog/product/cache/1/image/9df78eab33525d08d6e5fb8d27136e95/S/T/ST9020-SLG-2XL_-_Image_3.jpg', 'https://www.legendlife.com.au/media/catalog/product/cache/1/image/9df78eab33525d08d6e5fb8d27136e95/S/T/ST9020-WHI-2XL_-_Image_3.jpg'], 'variants': [{'color': 'Black Opal', 'size': 'S', 'stock': '500+'}, {'color': 'Black Opal', 'size': 'M', 'stock': '500+'}, {'color': 'Black Opal', 'size': 'L', 'stock': '500+'}, {'color': 'Black Opal', 'size': 'XL', 'stock': '500+'}, {'color': 'Black Opal', 'size': '2XL', 'stock': '500+'}, {'color': 'Crimson Red', 'size': 'S', 'stock': '500+'}, {'color': 'Crimson Red', 'size': 'M', 'stock': '500+'}, {'color': 'Crimson Red', 'size': 'L', 'stock': '500+'}, {'color': 'Crimson Red', 'size': 'XL', 'stock': '500+'}, {'color': 'Daisy Yellow', 'size': 'S', 'stock': '72'}, {'color': 'Daisy Yellow', 'size': 'M', 'stock': '48'}, {'color': 'Daisy Yellow', 'size': 'L', 'stock': '144'}, {'color': 'Daisy Yellow', 'size': 'XL', 'stock': '48'}, {'color': 'Deep Lilac', 'size': 'S', 'stock': '500+'}, {'color': 'Deep Lilac', 'size': 'M', 'stock': '500+'}, {'color': 'Deep Lilac', 'size': 'L', 'stock': '500+'}, {'color': 'Deep Lilac', 'size': 'XL', 'stock': '500+'}, {'color': 'Green Flash', 'size': 'S', 'stock': '500+'}, {'color': 'Green Flash', 'size': 'M', 'stock': '360'}, {'color': 'Green Flash', 'size': 'L', 'stock': '96'}, {'color': 'Green Flash', 'size': 'XL', 'stock': '24'}, {'color': 'Grey Heather', 'size': 'S', 'stock': '336'}, {'color': 'Grey Heather', 'size': 'M', 'stock': '500+'}, {'color': 'Grey Heather', 'size': 'L', 'stock': '500+'}, {'color': 'Grey Heather', 'size': 'XL', 'stock': '500+'}, {'color': 'King Blue', 'size': 'S', 'stock': '500+'}, {'color': 'King Blue', 'size': 'M', 'stock': '500+'}, {'color': 'King Blue', 'size': 'L', 'stock': '500+'}, {'color': 'King Blue', 'size': 'XL', 'stock': '480'}, {'color': 'Marine Blue', 'size': 'S', 'stock': '240'}, {'color': 'Marine Blue', 'size': 'M', 'stock': '500+'}, {'color': 'Marine Blue', 'size': 'L', 'stock': '500+'}, {'color': 'Marine Blue', 'size': 'XL', 'stock': '500+'}, {'color': 'Military Green', 'size': 'S', 'stock': '500+'}, {'color': 'Military Green', 'size': 'M', 'stock': '500+'}, {'color': 'Military Green', 'size': 'L', 'stock': '500+'}, {'color': 'Military Green', 'size': 'XL', 'stock': '500+'}, {'color': 'Slate Grey', 'size': 'S', 'stock': '312'}, {'color': 'Slate Grey', 'size': 'M', 'stock': '500+'}, {'color': 'Slate Grey', 'size': 'L', 'stock': '500+'}, {'color': 'Slate Grey', 'size': 'XL', 'stock': '312'}, {'color': 'Slate Grey', 'size': '2XL', 'stock': '96'}, {'color': 'White', 'size': 'S', 'stock': '500+'}, {'color': 'White', 'size': 'M', 'stock': '500+'}, {'color': 'White', 'size': 'L', 'stock': '500+'}, {'color': 'White', 'size': 'XL', 'stock': '500+'}, {'color': 'White', 'size': '2XL', 'stock': '432'}]}]
        #[{'sku': '4379', 'link': 'https://www.legendlife.com.au/sports-visor.html', 'title': 'Sports Visor', 'lowest_price': '$5.90', 'tags': 'new', 'description': "<p>This sports visor has classic flowing lines. It's made from microfibre, keeping it light and ensuring you stay cool whilst on the move.</p><h4>Customise your order - Request a Quote</h4><p>Submit a quote request to receive pricing based on your logo branding and quantity you require. Bulk discounts apply.</p><h4>Colours</h4><p>Black, Navy, Red, White, White/Royal</p><h4>Marketing Info Sheet</h4><ul><li><a href='https://www.legendlife.com.au/media/EPI_MediaFolder/4379/Marketing%20Info%20Sheet/4379_Marketing%20Info%20Sheet.pdf' target='_blank' >4379_Marketing Info Sheet.pdf</a></li></ul>", 'product_image': ['https://www.legendlife.com.au/media/catalog/product/cache/1/image/438x438/9df78eab33525d08d6e5fb8d27136e95/4/3/4379_-_Image_12.jpg', 'https://www.legendlife.com.au/media/catalog/product/cache/1/image/9df78eab33525d08d6e5fb8d27136e95/4/3/4379-BL_-_Image_13.jpg', 'https://www.legendlife.com.au/media/catalog/product/cache/1/image/9df78eab33525d08d6e5fb8d27136e95/4/3/4379-NA_-_Image_13.jpg', 'https://www.legendlife.com.au/media/catalog/product/cache/1/image/9df78eab33525d08d6e5fb8d27136e95/4/3/4379-RE_-_Image_13.jpg', 'https://www.legendlife.com.au/media/catalog/product/cache/1/image/9df78eab33525d08d6e5fb8d27136e95/4/3/4379-WH_-_Image_13.jpg', 'https://www.legendlife.com.au/media/catalog/product/cache/1/image/9df78eab33525d08d6e5fb8d27136e95/4/3/4379-WH.RO_-_Image_13.jpg'], 'variants': [{'color': 'Black', 'size': '', 'stock': '1000+'}, {'color': 'Navy', 'size': '', 'stock': '1000+'}, {'color': 'Red', 'size': '', 'stock': '36'}, {'color': 'White', 'size': '', 'stock': '1000+'}, {'color': 'White,Royal', 'size': '', 'stock': '61'}]}]

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
                    print(f'{products[i]["sku"]}.{products[i]["title"]}')
                    createNewProductLegendLife(products[i])
                else:
                    # Update existing product stock level 
                    print(f'updating ... {products[i]["sku"]}.{products[i]["title"]}')
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
                                                addInventoryLevel(vr["variant"]["inventory_item_id"],v_["stock"])
                                                time.sleep(1)
                                            except:
                                                continue
                              
                    except:
                        print(p)
                        print(products[i]["name"])
                        pass
if __name__ == "__main__":
    execution()

