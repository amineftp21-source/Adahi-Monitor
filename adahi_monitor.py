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

# تأمين دعم اللغة العربية
sys.stdout.reconfigure(encoding='utf-8')

# --- الإعدادات ---
TARGET_URL = "https://adhahi.dz/register"
DISCORD_WEBHOOK = "https://discord.com/api/webhooks/1496878067644235927/cqpxhZd03Q7JGwYgn_vhbGQZ4LvUdVjXTpxCsjmFPGk4gVeYsavH_VMDlXN1PBn8IPTq"
MY_STATES = ["الجزائر", "بومرداس", "بجاية", "سطيف", "برج"]

def send_discord_msg(message):
    try:
        requests.post(DISCORD_WEBHOOK, json={"content": message}, timeout=10)
    except:
        pass

def run_monitor():
    options = Options()
    # إعدادات إجبارية لمنع خطأ الـ Timeout في GitHub
    options.add_argument("--headless=new") # استخدام النسخة الجديدة من headless
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-extensions")
    options.add_argument("--window-size=1920,1080")
    
    # تحسين استقرار الاتصال
    service = Service(ChromeDriverManager().install())
    driver = None
    
    try:
        print(f"[{time.strftime('%H:%M:%S')}] جاري تشغيل المتصفح...")
        driver = webdriver.Chrome(service=service, options=options)
        
        # ضبط مهلة انتظار الصفحة لتقليل الضغط
        driver.set_page_load_timeout(60)
        
        print(f"[{time.strftime('%H:%M:%S')}] الدخول للموقع: {TARGET_URL}")
        driver.get(TARGET_URL)
        
        wait = WebDriverWait(driver, 40)
        
        # النقر على القائمة (نفس طريقتك)
        input_field = wait.until(EC.element_to_be_clickable((By.ID, "reg-wilaya")))
        driver.execute_script("arguments[0].scrollIntoView();", input_field)
        time.sleep(2)
        driver.execute_script("arguments[0].click();", input_field)
        
        # استخدام XPath الذي تفضله للبحث عن القائمة
        listbox_xpath = "//ul[@role='listbox']"
        wait.until(EC.presence_of_element_located((By.XPATH, listbox_xpath)))
        
        print("📡 جاري فحص الولايات...")
        time.sleep(10) # وقت كافٍ لتحميل البيانات

        items = driver.find_elements(By.XPATH, "//ul[@role='listbox']//li")
        
        if not items:
            print("⚠️ القائمة فارغة حالياً.")
            return

        print(f"✅ تم العثور على {len(items)} ولاية.")
        
        for item in items:
            wilaya_text = item.text.strip()
            if not wilaya_text: continue
            
            for state in MY_STATES:
                if state in wilaya_text:
                    if "متوفر" in wilaya_text or "disponible" in wilaya_text.lower():
                        msg = f"📢 @everyone **عاجل: توفر الحجز في {wilaya_text}!**\n{TARGET_URL}"
                        print(msg)
                        send_discord_msg(msg)
                        return 
                    else:
                        print(f"⏳ {wilaya_text}: غير متاح.")

    except Exception as e:
        # طباعة الخطأ بشكل مختصر لتسهيل التصحيح
        print(f"❌ حدث خطأ: {str(e)[:100]}")
    finally:
        if driver:
            driver.quit()
            print("🚪 إغلاق المتصفح.")

if __name__ == "__main__":
    run_monitor()
