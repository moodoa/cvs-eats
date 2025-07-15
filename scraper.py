import requests
import json
import os

def scrape_cmno_list():
    list_api_url = "https://foodsafety.family.com.tw/Web_FFD_2022/ws/QueryFsProductListByFilter"
    list_headers = {
        'Accept': 'application/json, text/plain, */*',
        'Content-Type': 'application/json',
        'Origin': 'https://foodsafety.family.com.tw',
        'Referer': 'https://foodsafety.family.com.tw/Web_FFD_2022/',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest',
    }
    list_payload = json.dumps({"MEMBER": "N", "KEYWORD": "", "INCLUDE_CLB": "Y"})

    list_response = requests.post(list_api_url, headers=list_headers, data=list_payload)
    list_response.raise_for_status()
    list_data = list_response.json()
    
    cmno_list = []
    if 'LIST' in list_data:
        for category in list_data['LIST']:
            if 'ITEM' in category:
                for item in category['ITEM']:
                    cmno_list.append({
                        'CMNO': item.get('CMNO', ''),
                        'PRODNAME': item.get('PRODNAME', ''),
                    })

    if not cmno_list:
        print("No product CMNOs found from the list API.")
        return

    output_path = os.path.join(os.path.dirname(__file__), 'cmno_list.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(cmno_list, f, ensure_ascii=False, indent=4)
    
    print(f"CMNO list scraped and saved to {output_path} successfully.")

if __name__ == "__main__":
    scrape_cmno_list()