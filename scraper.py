import os
import requests
from playwright.sync_api import sync_playwright

# 你的 GAS Web App 部署網址
GAS_URL = "https://script.google.com/macros/s/AKfycbzeyxhfqpJAx7mnpBmQty7OBfSFPNVogol9AD0ert00ya0YfEEO16GE4pJNu_6W_wWD/exec"

def scrape_tabelog():
    target_url = "https://s.tabelog.com/tokyo/A1304/A130401/13243161/" # 測試目標：以牛舌的檸檬為例
    
    with sync_playwright() as p:
        # 啟動雲端瀏覽器
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        
        print(f"正在前往抓取：{target_url}")
        page.goto(target_url, timeout=60000)
        page.wait_for_timeout(3000) # 修正為正確的 API
        
        # 抓取欄位資料
        data = {
            "source": "Tabelog",
            "url": target_url,
            "name": "",
            "rating": "",
            "review_count": "",
            "address": "",
            "business_hours": ""
        }
        
        try:
            # 1. 抓取店名
            name_el = page.query_selector("h2, .rstdtl-header-target, .display-name")
            data["name"] = name_el.inner_text().strip() if name_el else "未命名景點"
            
            # 2. 抓取評分
            rating_el = page.query_selector(".rd-rating-val, .c-rating__val")
            data["rating"] = rating_el.inner_text().strip() if rating_el else ""
            
            # 3. 抓取評論數
            review_el = page.query_selector("a[href*='rvw'] span, .rstdtl-rvw-count")
            data["review_count"] = review_el.inner_text().strip() if review_el else ""
            
            # 4. 抓取地址
            addr_el = page.query_selector(".rst-address, .rst-details-table__address")
            data["address"] = addr_el.inner_text().strip() if addr_el else ""
            
            # 5. 抓取營業時間
            hours_el = page.query_selector(".rst-details-table__opening-hours, [class*='opening-hours']")
            data["business_hours"] = hours_el.inner_text().strip() if hours_el else "請參考網頁"
            
        except Exception as e:
            print(f"解析 DOM 時發生錯誤: {e}")
            
        browser.close()
        
        # 將抓到的資料發送到 GAS Inbox
        send_to_gas(data)

def send_to_gas(data):
    print(f"正在傳送資料至 Google Sheets Inbox: {data['name']}")
    try:
        response = requests.post(GAS_URL, data=data)
        result = response.json()
        if result.get("status") == "success":
            print("✅ 成功寫入 Inbox！")
        else:
            print(f"❌ 寫入失敗：{result.get('message')}")
    except Exception as e:
        print(f"❌ 傳送至 GAS 發生網路錯誤：{e}")

if __name__ == "__main__":
    scrape_tabelog()
