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

# --- إعدادات المراقبة والتنبيه ---
TARGET_URL = "https://adhahi.dz/register"
# رابط الويب هوك الخاص بك على ديسكورد
DISCORD_WEBHOOK = "https://discord.com/api/webhooks/1496878067644235927/cqpxhZd03Q7JGwYgn_vhbGQZ4LvUdVjXTpxCsjmFPGk4gVeYsavH_VMDlXN1PBn8IPTq"

# الولايات المطلوبة (استخدمنا كلمات مفتاحية لتجنب مشاكل الهمزة)
MY_STATES = ["جزائر", "بومرداس", "بجاية", "سطيف", "برج"]

def send_discord_msg(message):
    """إرسال تنبيه إلى ديسكورد"""
    payload = {"content": message}
    try:
        requests.post(DISCORD_WEBHOOK, json=payload, timeout=10)
        print("✅ تم إرسال التنبيه إلى ديسكورد!")
    except Exception as e:
        print(f"⚠️ فشل إرسال التنبيه: {e}")

def run_monitor():
    options = Options()
    # إعدادات إجبارية للعمل في GitHub Actions
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    
    # محاكاة متصفح حقيقي لتجنب الحظر
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    try:
        print(f"\n[{time.strftime('%H:%M:%S')}] جاري فحص المنصة...")
        driver.get(TARGET_URL)
        
        wait = WebDriverWait(driver, 40)
        
        # الانتظار والنقر على قائمة الولايات
        input_field = wait.until(EC.element_to_be_clickable((By.ID, "reg-wilaya")))
        driver.execute_script("arguments[0].scrollIntoView();", input_field)
        time.sleep(2)
        driver.execute_script("arguments[0].click();", input_field)
        
        # انتظار ظهور القائمة المنسدلة (باستخدام نفس المنطق الخاص بك)
        listbox_xpath = "//ul[@role='listbox']"
        wait.until(EC.presence_of_element_located((By.XPATH, listbox_xpath)))
        time.sleep(10) # وقت إضافي لتحميل البيانات

        items = driver.find_elements(By.XPATH, "//ul[@role='listbox']//li")
        
        if not items:
            print("⚠️ القائمة مفتوحة لكن لم تظهر الولايات بعد.")
            return

        print(f"✅ تم العثور على {len(items)} ولاية في القائمة.")
        
        for item in items:
            wilaya_text = item.text.strip()
            if not wilaya_text: continue
            
            for state in MY_STATES:
                if state in wilaya_text:
                    if "متوفر" in wilaya_text or "disponible" in wilaya_text.lower():
                        alert_msg = f"📢 @everyone **مبروك! متوفر الآن:** {wilaya_text}\nرابط الحجز: {TARGET_URL}"
                        print(alert_msg)
                        send_discord_msg(alert_msg)
                        return 
                    else:
                        print(f"⏳ حالة {wilaya_text}: غير متوفر.")

    except Exception as e:
        print(f"❌ حدث خطأ أثناء الفحص: {str(e)[:100]}")
    finally:
        driver.quit()

if __name__ == "__main__":
    run_monitor()
