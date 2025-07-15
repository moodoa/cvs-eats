import requests

import re
import json

with open("cmno_list.json", "r") as f:
    cmnos = json.load(f)

products = []

for item in cmnos:
    try:
        print(f"Processing {item['PRODNAME']}...")
        product = {}
        data = requests.post("https://foodsafety.family.com.tw/Web_FFD_2022/ws/QueryFsProductByItem", data={"CMNO": item["CMNO"]}).json()
        note = data["LIST"][0]["NOTE"]
        match = re.search(r"熱量(\d+)大卡", note)
        heat = int(match.group(1)) if match else None
        nutrients = data["LIST"][0]["NUTRIENTS"][0]
        product["name"] = item["PRODNAME"]
        product["heat"] = heat
        product["carbs"] = nutrients["CARBOHYDRATE"]
        product["protein"] = nutrients["PROTEIN"]
        product["fat"] = nutrients["TOTALFAT"]
        product["sat_fat"] = nutrients["SATFAT"]
        product["trans_fat"] = nutrients["TRANSFAT"]
        product["sodium"] = nutrients["SODIUM"]
        product["sugar"] = nutrients["SUGAR"]
        products.append(product)
    except:
        pass

with open("products.json", "w") as f:
    json.dump(products, f, ensure_ascii=False, indent=4)



