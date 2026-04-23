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

# تأمين اللغة العربية
sys.stdout.reconfigure(encoding='utf-8')

# --- إعداداتك ---
DISCORD_WEBHOOK = "https://discord.com/api/webhooks/1496878067644235927/cqpxhZd03Q7JGwYgn_vhbGQZ4LvUdVjXTpxCsjmFPGk4gVeYsavH_VMDlXN1PBn8IPTq"
MY_STATES = ["ادرار", "بجاية", "سطيف", "برج بوعريريج"]

def send_discord(message):
    payload = {"content": message}
    try:
        requests.post(DISCORD_WEBHOOK, json=payload)
        print("✅ أرسلت التنبيه إلى ديسكورد!")
    except Exception as e:
        print(f"❌ فشل الإرسال لديسكورد: {e}")

def check_site():
    chrome_options = Options()
    # إعدادات إجبارية للعمل على GitHub Actions
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    try:
        print(f"[{time.strftime('%H:%M:%S')}] جاري فحص المنصة...")
        driver.get("https://adhahi.dz/register")
        wait = WebDriverWait(driver, 45)
        
        # الضغط على القائمة
        input_field = wait.until(EC.element_to_be_clickable((By.ID, "reg-wilaya")))
        driver.execute_script("arguments[0].click();", input_field)
        
        time.sleep(5) # انتظار تحميل الولايات من السيرفر
        
        items = driver.find_elements(By.TAG_NAME, "li")
        
        if len(items) > 10:
            for item in items:
                text = item.text.strip()
                for state in MY_STATES:
                    if state in text and "حجز متوفر" in text:
                        msg = f"📢 @everyone **عاجل: توفرت الأضاحي في {text}!**\nرابط التسجيل: https://adhahi.dz/register"
                        send_discord(msg)
                        return
            print("⏳ الولايات المطلوبة مغلقة حالياً.")
        else:
            print("⚠️ القائمة فارغة (الموقع ثقيل).")
            
    except Exception as e:
        print(f"❌ حدث خطأ أثناء الفحص: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    check_site()
