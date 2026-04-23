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

DISCORD_WEBHOOK = "https://discord.com/api/webhooks/1496878067644235927/cqpxhZd03Q7JGwYgn_vhbGQZ4LvUdVjXTpxCsjmFPGk4gVeYsavH_VMDlXN1PBn8IPTq"
MY_STATES = ["درار", "بجاية", "سطيف", "برج"]

def send_discord(message):
    try:
        requests.post(DISCORD_WEBHOOK, json={"content": message}, timeout=10)
    except:
        pass

def run_check():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    # --- الحل السحري للـ Timeout ---
    options.page_load_strategy = 'eager' # لا تنتظر تحميل الصور والملفات الثقيلة
    options.add_argument("--blink-settings=imagesEnabled=false") # تسريع الموقع بمنع الصور
    
    driver = None
    try:
        print(f"[{time.strftime('%H:%M:%S')}] تشغيل المحرك السحابي...")
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        
        # ضبط مهلة قصيرة للتحميل لمنع التجمد الطويل
        driver.set_page_load_timeout(30) 
        
        print(f"[{time.strftime('%H:%M:%S')}] محاولة الدخول السريع للموقع...")
        try:
            driver.get("https://adhahi.dz/register")
        except Exception:
            print("⚠️ تم تجاوز مهلة التحميل الكاملة (سنحاول العمل بما تم تحميله)")

        wait = WebDriverWait(driver, 40)
        
        # محاولة العثور على القائمة
        print("🔍 البحث عن قائمة الولايات...")
        input_field = wait.until(EC.presence_of_element_located((By.ID, "reg-wilaya")))
        
        # استخدام JavaScript للنقر لتجنب مشاكل الـ Renderer
        driver.execute_script("arguments[0].click();", input_field)
        
        time.sleep(12) # وقت كافٍ جداً لجلب البيانات من السيرفر

        items = driver.find_elements(By.TAG_NAME, "li")
        
        if len(items) < 5:
            print("⚠️ القائمة لم تكتمل بعد، إعادة المحاولة في الدورة القادمة.")
            return

        for item in items:
            text = item.text.strip()
            if any(state in text for state in MY_STATES):
                if "متوفر" in text or "disponible" in text.lower():
                    send_discord(f"📢 @everyone **حجز متاح الآن في: {text}!**\nhttps://adhahi.dz/register")
                    print(f"✅ تم العثور على هدف: {text}")
                    return
                else:
                    print(f"⏳ {text}: غير متاح.")
                    
    except Exception as e:
        print(f"❌ خطأ غير متوقع: {str(e)[:100]}") # طباعة جزء من الخطأ للاختصار
    finally:
        if driver:
            driver.quit()
            print("🚪 إغلاق آمن للمتصفح.")

if __name__ == "__main__":
    run_check()
