import requests
import json
import pprint
import os
import logging

client_id = os.environ['CLIENT_ID']
refresh_token = os.environ['REFRESH_TOKEN']
url_promobrand=os.environ['URL_PROMOBRAND']
cookie_promobrand=os.environ['COOKIE_PROMOBRAND']
api_promobrand=os.environ['API_PROMOBRAND']

logger = logging.getLogger(__name__)
def gettoken():
    url = url_promobrand

    querystring = {"grant_type":"refresh_token","client_id":client_id,"refresh_token":refresh_token}

    headers = {
        "cookie": cookie_promobrand,
        "Content-Type": "application/x-www-form-urlencoded"
    }

    response = requests.request("POST", url, headers=headers, params=querystring)
    token = json.loads(response.text)["id_token"]
    return token

def getPromoBrandProducts(token, id):
    url_ = api_promobrand
    querystring = {"After": id}
    headers_ = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }

    response_ = requests.request("GET", url_, headers=headers_, params=querystring)
    products = json.loads(response_.text)
    listObj = []
    tags =""
    for i in products:
        # Add variants
        variants = []
        # if len(i["Inventory"]) ==0:
        #     variants.append({
        #         "stock": "1",
        #         "color": "New",
        #         "itemNumber":i["Product_Code"]
        #     })
        #     tags = "new"
        # else:
        tags =i["APPA_Categories"]
        for v in i["Inventory"]:

            # usually item dont have variant color == None, bypass item Name instead
            color = v["InventoryDetails"]["colour"]
            if color == None: color = v["InventoryDetails"]["itemName"]

            variants.append({
                "stock": v["InventoryDetails"]["onHand"],
                "color": color,
                "itemNumber": v["InventoryDetails"]["itemNumber"]
            })
        # Add images
        images = []
        if i["Product_Images"]["productBrandedImages"] is not None:
            for im in i["Product_Images"]["productBrandedImages"]:
                images.append({
                    im["mediaItemUrl"]
                })
        if i["Product_Images"]["productPackagingImages"] is not None:
            for im1 in i["Product_Images"]["productPackagingImages"]:
                images.append({
                    im1["mediaItemUrl"]
                })
        if i["Product_Images"]["productUnbrandedImages"] is not None:
            for im2 in i["Product_Images"]["productUnbrandedImages"]:
                images.append({
                    im2["mediaItemUrl"]
                })
        # Add to product list
        listObj.append({
            "product_id": i['Product_ID'],
            "product_code": i["Product_Code"],
            "name": i["Name"],
            "description": i["Description"],
            "lowest_price": i["Lowest_Price"],
            "product_image": images,
            "variants": variants,
            "tags": tags
            })
    print(f"Promobrands total products {len(listObj)}")
    return listObj

def promo_brands():
    token = gettoken()
    # Run loop for pagination
    last_product = 0 
    res = getPromoBrandProducts(token, last_product)
    while len(res) != 0:
        res = getPromoBrandProducts(token, last_product)
        last_product = res[len(res)]["Product_ID"]
        print(last_product)

        return res
    
