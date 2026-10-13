import os
import requests
from playwright.sync_api import sync_playwright
from playwright_stealth import stealth_sync

GAS_URL = "https://script.google.com/macros/s/AKfycbzeyxhfqpJAx7mnpBmQty7OBfSFPNVogol9AD0ert00ya0YfEEO16GE4pJNu_6W_wWD/exec"

def scrape_tabelog():
    target_url = "https://s.tabelog.com/tokyo/A1304/A130401/13243161/"
    
    with sync_playwright() as p:
        # 以「非無頭模式的隱藏參數」啟動，並模擬真實使用者視窗與日本當地語系
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--start-maximized",
                "--no-sandbox",
                "--disable-setuid-sandbox"
            ]
        )
        
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080},
            locale="ja-JP",
            timezone_id="Asia/Tokyo"
        )
        
        page = context.new_page()
        
        # 🔑 關鍵：注入 Stealth 隱身腳本，抹除所有 Playwright 機器人特徵
        stealth_sync(page)
        
        print(f"正在前往抓取（隱身模式）：{target_url}")
        try:
            page.goto(target_url, timeout=60000, wait_until="domcontentloaded")
            page.wait_for_timeout(5000) # 給予足夠時間讓頁面渲染
        except Exception as e:
            print(f"網頁載入超時或失敗: {e}")
        
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
            # 抓取欄位
            name_el = page.query_selector("h2, .rstdtl-header-target, .display-name")
            data["name"] = name_el.inner_text().strip() if name_el else "未命名景點"
            
            rating_el = page.query_selector(".rd-rating-val, .c-rating__val")
            data["rating"] = rating_el.inner_text().strip() if rating_el else ""
            
            review_el = page.query_selector("a[href*='rvw'] span, .rstdtl-rvw-count")
            data["review_count"] = review_el.inner_text().strip() if review_el else ""
            
            addr_el = page.query_selector(".rst-address, .rst-details-table__address")
            data["address"] = addr_el.inner_text().strip() if addr_el else ""
            
            hours_el = page.query_selector(".rst-details-table__opening-hours, [class*='opening-hours']")
            data["business_hours"] = hours_el.inner_text().strip() if hours_el else "請參考網頁"
            
        except Exception as e:
            print(f"解析 DOM 時發生錯誤: {e}")
            
        browser.close()
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
