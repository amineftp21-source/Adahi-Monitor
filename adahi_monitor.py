import sys
import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

sys.stdout.reconfigure(encoding='utf-8')

TARGET_URL = "https://adhahi.dz/register"
DISCORD_WEBHOOK = "https://discord.com/api/webhooks/1496878067644235927/cqpxhZd03Q7JGwYgn_vhbGQZ4LvUdVjXTpxCsjmFPGk4gVeYsavH_VMDlXN1PBn8IPTq"
MY_STATES = ["جزائر", "بومرداس", "بجاية", "سطيف", "برج"]

def send_discord_msg(message):
    try:
        requests.post(DISCORD_WEBHOOK, json={"content": message}, timeout=10)
    except: pass

def run_monitor():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    
    # تحسينات جذرية لمنع الـ Renderer Timeout
    options.add_argument("--disable-software-rasterizer")
    options.add_argument("--disable-extensions")
    options.add_argument("--blink-settings=imagesEnabled=false")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
    
    # استراتيجية تحميل تمنع التعليق
    options.page_load_strategy = 'none' 

    driver = None
    try:
        print(f"[{time.strftime('%H:%M:%S')}] محاولة الاختراق السريع للموقع...")
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        
        # نفتح الموقع وننتظر يدوياً بدلاً من ترك المتصفح يعلق
        driver.get(TARGET_URL)
        
        # انتظار يدوي مرن لظهور الهيكل
        found = False
        for i in range(15): # انتظر حتى 30 ثانية
            time.sleep(2)
            if "reg-wilaya" in driver.page_source:
                found = True
                break
            print("⏳ في انتظار استجابة السيرفر...")

        if not found:
            print("❌ الموقع لم يستجب في الوقت المحدد.")
            return

        # محاولة النقر المباشر عبر جافا سكريبت (تتخطى مشاكل الرسم)
        print("🔍 محاولة فتح قائمة الولايات...")
        driver.execute_script("document.getElementById('reg-wilaya').click();")
        
        time.sleep(10) # وقت لتحميل الولايات

        items = driver.find_elements(By.TAG_NAME, "li")
        print(f"📊 النتائج المكتشفة: {len(items)} عنصر.")

        for item in items:
            text = item.text.strip()
            if any(state in text for state in MY_STATES):
                if "متوفر" in text or "disponible" in text.lower():
                    send_discord_msg(f"📢 @everyone **حجز متاح الآن في: {text}!**\n{TARGET_URL}")
                    print(f"✅ تم العثور على حجز في {text}")
                    return
                else:
                    print(f"⏳ {text}: غير متاح.")

    except Exception as e:
        print(f"⚠️ خطأ بسيط: {str(e)[:50]}")
    finally:
        if driver:
            driver.quit()
            print("🚪 إغلاق المتصفح.")

if __name__ == "__main__":
    run_monitor()
