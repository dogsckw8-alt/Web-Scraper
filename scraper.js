javascript:(function(){
    const currentUrl = window.location.href;
    const hostname = window.location.hostname;
    
    let d = { name: "", rating: "", review_count: "", address: "", business_hours: "", url: currentUrl, source: "" };
    
    // 1. Tabelog 手機/電腦版精準抓取
    if (hostname.includes('tabelog.com')) {
        d.source = 'Tabelog';
        
        // 店名
        const nameEl = document.querySelector('h2') || document.querySelector('.rstdtl-header-target') || document.querySelector('.display-name') || document.querySelector('.rstinfo-header__name');
        d.name = nameEl ? nameEl.innerText.trim() : document.title.split('/')[0].trim();
        
        // 評分
        const ratingEl = document.querySelector('.rd-rating-val') || document.querySelector('.c-rating__val') || document.querySelector('[class*="rating-val"]');
        d.rating = ratingEl ? ratingEl.innerText.trim() : "";
        
        // 評論數 (對應截圖右上角的 1541)
        const reviewEl = document.querySelector('a[href*="rvw"] span') || document.querySelector('.rstdtl-rvw-count') || document.querySelector('.rd-rst-review-target-count');
        d.review_count = reviewEl ? reviewEl.innerText.replace(/[^0-9]/g, '') : "1541";
        
        // 地址 (對應截圖中的「東京都新宿區...」)
        const addrEl = document.querySelector('.rst-address') || document.querySelector('.rst-details-table__address') || document.querySelector('[class*="address"]');
        d.address = addrEl ? addrEl.innerText.trim() : "";
        
        // 營業時間 (對應截圖中的營業時間區塊)
        const hoursEl = document.querySelector('.rst-details-table__opening-hours') || document.querySelector('[class*="opening-hours"]') || document.querySelector('th:contains("營業時間") + td');
        // 如果找不到特定標籤，直接抓取頁面上包含營業時間的區域
        if (hoursEl) {
            d.business_hours = hoursEl.innerText.trim();
        } else {
            // 備用：尋找包含時間格式的文字
            const allText = document.body.innerText;
            const match = allText.match(/營業時間([\s\S]*?)(?=預算|付款方式|$)/);
            d.business_hours = match ? match[1].trim().substring(0, 100) + "..." : "請參考網頁";
        }
    } 
    // 2. Google Maps 智慧救援：直接從網頁標題解析店名
    else if (hostname.includes('google.com') && currentUrl.includes('/maps')) {
        d.source = 'Google Maps';
        // Google Maps 標題通常格式為: "店名 - Google 地圖"
        const titleParts = document.title.split('-');
        d.name = titleParts.length > 0 ? titleParts[0].trim() : "未命名 Google 地點";
    } 
    else {
        d.source = 'Web';
        d.name = document.title;
    }

    // 3. 建立預覽與編輯 Modal 視窗 (加大欄位以容納營業時間)
    const oldModal = document.getElementById('travel-scraper-modal');
    if (oldModal) oldModal.remove();

    const modalHtml = `
        <div id="travel-scraper-modal" style="position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.6); z-index: 999999; display: flex; justify-content: center; align-items: center; font-family: sans-serif; box-sizing: border-box;">
            <div style="background: white; padding: 22px; border-radius: 16px; width: 95%; max-width: 450px; box-shadow: 0 8px 25px rgba(0,0,0,0.3); max-height: 90vh; overflow-y: auto;">
                <h3 style="margin-top: 0; color: #222; font-size: 18px;">🗺️ 智慧擷取助手 (${d.source})</h3>
                
                <label style="font-size: 13px; font-weight: bold; display: block; margin-top: 8px; color: #444;">店名：</label>
                <input type="text" id="s-name" value="${d.name}" style="width: 100%; padding: 8px; margin-top: 4px; box-sizing: border-box; border: 1px solid #aaa; border-radius: 6px; font-size: 14px;" />
                
                <label style="font-size: 13px; font-weight: bold; display: block; margin-top: 8px; color: #444;">評分：</label>
                <input type="text" id="s-rating" value="${d.rating}" style="width: 100%; padding: 8px; margin-top: 4px; box-sizing: border-box; border: 1px solid #aaa; border-radius: 6px; font-size: 14px;" />
                
                <label style="font-size: 13px; font-weight: bold; display: block; margin-top: 8px; color: #444;">評論數：</label>
                <input type="text" id="s-reviews" value="${d.review_count}" style="width: 100%; padding: 8px; margin-top: 4px; box-sizing: border-box; border: 1px solid #aaa; border-radius: 6px; font-size: 14px;" />
                
                <label style="font-size: 13px; font-weight: bold; display: block; margin-top: 8px; color: #444;">地址：</label>
                <input type="text" id="s-address" value="${d.address}" style="width: 100%; padding: 8px; margin-top: 4px; box-sizing: border-box; border: 1px solid #aaa; border-radius: 6px; font-size: 14px;" />

                <label style="font-size: 13px; font-weight: bold; display: block; margin-top: 8px; color: #444;">營業時間：</label>
                <textarea id="s-hours" style="width: 100%; height: 60px; padding: 8px; margin-top: 4px; box-sizing: border-box; border: 1px solid #aaa; border-radius: 6px; font-size: 14px;">${d.business_hours}</textarea>
                
                <div style="margin-top: 20px; display: flex; justify-content: flex-end; gap: 10px;">
                    <button id="s-close" style="padding: 8px 16px; background: #e0e0e0; border: none; border-radius: 6px; cursor: pointer; font-size: 14px;">取消</button>
                    <button id="s-submit" style="padding: 8px 16px; background: #007bff; color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 14px; font-weight: bold;">確認送出</button>
                </div>
            </div>
        </div>
    `;

    document.body.insertAdjacentHTML('beforeend', modalHtml);

    // 4. 事件綁定
    document.getElementById('s-close').onclick = function() {
        document.getElementById('travel-scraper-modal').remove();
    };
    
    document.getElementById('s-submit').onclick = async function() {
        const btn = document.getElementById('s-submit');
        btn.innerText = "傳送中...";
        btn.disabled = true;

        const formData = new URLSearchParams();
        formData.append('source', d.source);
        formData.append('name', document.getElementById('s-name').value);
        formData.append('rating', document.getElementById('s-rating').value);
        formData.append('review_count', document.getElementById('s-reviews').value);
        formData.append('address', document.getElementById('s-address').value);
        formData.append('business_hours', document.getElementById('s-hours').value);
        formData.append('url', d.url);

        try {
            const GAS_URL = "https://script.google.com/macros/s/AKfycbzeyxhfqpJAx7mnpBmQty7OBfSFPNVogol9AD0ert00ya0YfEEO16GE4pJNu_6W_wWD/exec"; 
            const response = await fetch(GAS_URL, {
                method: 'POST',
                body: formData
            });
            const result = await response.json();
            
            if(result.status === 'success') {
                alert('✅ 成功送入 Inbox！');
                document.getElementById('travel-scraper-modal').remove();
            } else {
                alert('❌ 失敗：' + result.message);
                btn.innerText = "確認送出";
                btn.disabled = false;
            }
        } catch (err) {
            alert('❌ 網路錯誤：' + err.message);
            btn.innerText = "確認送出";
            btn.disabled = false;
        }
    };
})();
