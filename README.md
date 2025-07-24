# CVS EATS

CVS EATS 是一個基於 Flask 的網路應用程式，旨在幫助使用者根據個人營養目標（蛋白質、熱量、鈉）從便利商店的食品中推薦合適的餐點組合。

try it: https://cvs-eats.onrender.com

## 功能特色

*   **智慧餐點推薦**：根據使用者輸入的蛋白質目標、熱量上限和鈉上限，自動生成符合條件的食品組合。
*   **營養資訊總覽**：顯示推薦餐點組合的總熱量、蛋白質、脂肪、鈉和糖等詳細營養資訊。
*   **直觀的使用者介面**：透過簡單的網頁表單輸入，即可獲得推薦結果。
*   **食品資料爬取**：包含一個爬蟲工具，用於從外部來源獲取便利商店的商品資料。

## 安裝指南

請依照以下步驟在您的本地環境中設定並運行此專案：

1.  **複製專案**：
    ```bash
    git clone https://github.com/your-username/cvs-eats.git
    cd cvs-eats
    ```

2.  **建立並啟用虛擬環境**：
    ```bash
    python3 -m venv env
    source env/bin/activate  # macOS/Linux
    # 或 `.\env\Scripts\activate` (Windows)
    ```

3.  **安裝依賴套件**：
    ```bash
    pip install -r requirements.txt
    ```
    如果 `requirements.txt` 不存在，您可能需要手動安裝 Flask 和 Requests：
    ```bash
    pip install Flask requests
    ```

4.  **準備食品資料**：
    本應用程式依賴 `products.json` 檔案來獲取食品營養資料。您可以運行 `scraper.py` 來獲取部分商品資訊，但您可能需要手動建立或補充 `products.json` 檔案，使其包含詳細的營養數據。
    ```bash
    python scraper.py
    # 這將生成 cmno_list.json，您可能需要 cmno_to_products.py 或手動處理來生成 products.json
    ```
    `products.json` 的格式應如下所示：
    ```json
    [
        {
            "name": "食品A",
            "heat": 200,
            "protein": 10,
            "fat": 5,
            "sat_fat": 2,
            "trans_fat": 0,
            "sodium": 300,
            "sugar": 15
        },
        {
            "name": "食品B",
            "heat": 350,
            "protein": 20,
            "fat": 15,
            "sat_fat": 5,
            "trans_fat": 0,
            "sodium": 500,
            "sugar": 10
        }
    ]
    ```

## 使用方式

1.  **啟動應用程式**：
    ```bash
    python app.py
    ```
    應用程式將會在 `http://127.0.0.1:5000/` 運行。

2.  **開啟瀏覽器**：
    在您的網頁瀏覽器中訪問 `http://127.0.0.1:5000/`。

3.  **輸入營養目標**：
    在網頁表單中輸入您希望的蛋白質目標、熱量上限和鈉上限，然後點擊「開始推薦」按鈕。

4.  **查看推薦結果**：
    應用程式將會顯示一個符合您條件的食品組合，並提供其總營養資訊。

## 專案結構

```
.
├── .gitignore
├── app.py              # Flask 應用程式主文件，處理網頁請求和餐點推薦邏輯
├── cmno_to_products.py # 可能用於將爬取的商品編號轉換為詳細產品資料
├── LICENSE             # 專案授權文件
├── products.json       # 儲存食品營養資料的 JSON 文件
├── README.md           # 專案說明文件
├── scraper.py          # 爬蟲工具，用於獲取便利商店商品列表
├── env/                # Python 虛擬環境目錄
├── static/
│   ├── app.js          # 前端 JavaScript，處理食物卡片互動
│   └── style.css       # 前端 CSS 樣式表
└── templates/
    └── index.html      # 網頁主頁面模板
```

## 版權宣告

本專案採用 [LICENSE](LICENSE) 文件中定義的授權條款。
