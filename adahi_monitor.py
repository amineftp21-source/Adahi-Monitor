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

# دعم اللغة العربية
sys.stdout.reconfigure(encoding='utf-8')

# --- إعدادات التنبيه ---
DISCORD_WEBHOOK = "https://discord.com/api/webhooks/1496878067644235927/cqpxhZd03Q7JGwYgn_vhbGQZ4LvUdVjXTpxCsjmFPGk4gVeYsavH_VMDlXN1PBn8IPTq"

# كلمات مفتاحية ذكية لتجنب مشاكل الهمزة في (أدرار/ادرار)
MY_STATES = [" درار", "بجاية", "سطيف", "برج بوعريريج"]

def send_discord(message):
    payload = {"content": message}
    try:
        requests.post(DISCORD_WEBHOOK, json=payload)
        print("✅ تم إرسال التنبيه لديسكورد!")
    except Exception as e:
        print(f"❌ فشل إرسال ديسكورد: {e}")

def run_check():
    options = Options()
    options.add_argument("--headless") # ضروري لـ GitHub
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    try:
        print(f"[{time.strftime('%H:%M:%S')}] بدء الفحص السحابي...")
        driver.get("https://adhahi.dz/register")
        wait = WebDriverWait(driver, 45)
        
        # الوصول للقائمة المنسدلة
        input_field = wait.until(EC.element_to_be_clickable((By.ID, "reg-wilaya")))
        driver.execute_script("arguments[0].click();", input_field)
        
        # انتظار كافٍ لضمان تحميل النصوص بالكامل
        time.sleep(7) 

        # البحث عن الولايات داخل عناصر li
        items = driver.find_elements(By.TAG_NAME, "li")
        
        if len(items) < 10:
            print("⚠️ القائمة فارغة أو الموقع لم يحمل بشكل كامل.")
            return

        found_any = False
        for item in items:
            text = item.text.strip()
            if not text: continue
            
            for state in MY_STATES:
                if state in text:
                    found_any = True
                    # التحقق من توفر الحجز
                    if "متوفر" in text or "disponible" in text.lower():
                        msg = f"📢 @everyone **عاجل: توفر الحجز في {text}!**\nاحجز الآن: https://adhahi.dz/register"
                        send_discord(msg)
                        return # الخروج بعد إرسال التنبيه
                    else:
                        print(f"⏳ {text}: لا يزال مغلقاً.")

        if not found_any:
            print("ℹ️ لم يتم العثور على الولايات المطلوبة في القائمة.")

    except Exception as e:
        print(f"❌ حدث خطأ تقني: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    run_check()
