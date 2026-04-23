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

# دعم العربية
sys.stdout.reconfigure(encoding='utf-8')

TARGET_URL = "https://adhahi.dz/register"
DISCORD_WEBHOOK = "https://discord.com/api/webhooks/1496878067644235927/cqpxhZd03Q7JGwYgn_vhbGQZ4LvUdVjXTpxCsjmFPGk4gVeYsavH_VMDlXN1PBn8IPTq"
MY_STATES = ["جزائر", "بومرداس", "بجاية", "سطيف", "برج"]

def send_discord_msg(message):
    try:
        requests.post(DISCORD_WEBHOOK, json={"content": message}, timeout=10)
    except:
        pass

def run_monitor():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    
    # --- التعديل الجوهري لحل مشكلة Renderer Timeout ---
    options.page_load_strategy = 'eager' # ابدأ العمل قبل اكتمال تحميل كل شيء
    options.add_argument("--blink-settings=imagesEnabled=false") # تسريع خيالي بمنع الصور
    
    driver = None
    try:
        print(f"[{time.strftime('%H:%M:%S')}] تشغيل المحرك السحابي...")
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        
        # ضبط مهلة قصيرة (30 ثانية) لأننا نستخدم eager
        driver.set_page_load_timeout(30)
        
        print(f"[{time.strftime('%H:%M:%S')}] دخول سريع للموقع...")
        try:
            driver.get(TARGET_URL)
        except:
            # نتجاهل التايم أوت ونكمل لأن 'eager' يكون قد جلب الهيكل الأساسي فعلاً
            pass
        
        wait = WebDriverWait(driver, 40)
        
        # البحث عن القائمة
        print("🔍 البحث عن حقل الولايات...")
        input_field = wait.until(EC.presence_of_element_located((By.ID, "reg-wilaya")))
        
        # النقر باستخدام جافا سكريبت لأنه الأضمن في حالات التجميد
        driver.execute_script("arguments[0].click();", input_field)
        
        print("📡 فحص الولايات (انتظار تحميل البيانات)...")
        time.sleep(12) 

        # منطق الـ XPath الخاص بك
        items = driver.find_elements(By.XPATH, "//ul[@role='listbox']//li")
        
        if not items:
            print("⚠️ القائمة لم تظهر، الموقع ثقيل جداً حالياً.")
            return

        print(f"✅ تم جلب {len(items)} ولاية.")
        
        for item in items:
            text = item.text.strip()
            if any(state in text for state in MY_STATES):
                if "متوفر" in text or "disponible" in text.lower():
                    msg = f"📢 @everyone **عاجل: توفر الحجز في {text}!**\n{TARGET_URL}"
                    send_discord_msg(msg)
                    print(f"✅ مبروك! هدف محقق: {text}")
                    return 
                else:
                    print(f"⏳ {text}: غير متاح.")

    except Exception as e:
        print(f"❌ خطأ تقني: {str(e)[:100]}")
    finally:
        if driver:
            driver.quit()
            print("🚪 إغلاق المتصفح.")

if __name__ == "__main__":
    run_monitor()
