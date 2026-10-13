import requests
from playwright.sync_api import sync_playwright

# 替換成你已部署好的 GAS Web App 網址
GAS_WEB_APP_URL = "https://script.google.com/macros/s/AKfycbzeyxhfqpJAx7mnpBmQty7OBfSFPNVogol9AD0ert00ya0YfEEO16GE4pJNu_6W_wWD/exec"


def scrape_google_maps(url):
  with sync_playwright() as p:
    # 啟動瀏覽器（headless=False 可以看見瀏覽器運作畫面，方便除錯）
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()

    print(f"正在前往 Google Maps 網頁: {url}")
    page.goto(url)

    # 給予頁面足夠時間載入動態內容
    page.wait_for_timeout(4000)

    title = ""
    rating = ""
    address = ""
    hours = ""

    try:
      # 1. 抓取店名
      title_el = page.locator("h1.DUwDvf")
      if title_el.count() > 0:
        title = title_el.inner_text().strip()

      # 2. 抓取評分
      rating_el = page.locator("div.F7nice span").first
      if rating_el.count() > 0:
        rating = rating_el.inner_text().strip()

      # 3. 抓取地址
      address_el = page.locator('button[data-item-id="address"] div')
      if address_el.count() > 0:
        address = address_el.inner_text().strip()

      # 4. 抓取營業時間
      hours_el = page.locator('div[data-item-id="oh"] div')
      if hours_el.count() > 0:
        hours = hours_el.inner_text().strip()

    except Exception as e:
      print(f"⚠️ 選擇器解析時發生例外: {e}")

    browser.close()

    # 組裝資料並透過 GET 傳遞給你的 GAS 接收器
    payload = {
        "url": url,
        "title": title,
        "rating": rating,
        "address": address,
        "hours": hours,
    }

    try:
      response = requests.get(GAS_WEB_APP_URL, params=payload)
      print(f"✅ 成功同步至試算表！餐廳：{title} | 回應：{response.text}")
    except Exception as e:
      print(f"❌ 同步至 GAS 失敗：{e}")


if __name__ == "__main__":
  # 請替換成你想測試的 Google Maps 餐廳網址
  test_url = "你的_Google_Maps_餐廳網址"
  scrape_google_maps(test_url)
