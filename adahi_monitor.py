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

# دعم اللغة العربية في مخرجات GitHub
sys.stdout.reconfigure(encoding='utf-8')

# --- إعداداتك الخاصة ---
DISCORD_WEBHOOK = "https://discord.com/api/webhooks/1496878067644235927/cqpxhZd03Q7JGwYgn_vhbGQZ4LvUdVjXTpxCsjmFPGk4gVeYsavH_VMDlXN1PBn8IPTq"

# كلمات مفتاحية ذكية: "درار" تجلب (أدرار/ادرار)، و"برج" تجلب (برج بوعريريج)
MY_STATES = ["درار", "بجاية", "سطيف", "برج"]

def send_discord(message):
    payload = {"content": message}
    try:
        response = requests.post(DISCORD_WEBHOOK, json=payload)
        if response.status_code == 204:
            print("✅ تم إرسال التنبيه إلى ديسكورد بنجاح!")
    except Exception as e:
        print(f"❌ فشل إرسال التنبيه: {e}")

def run_check():
    options = Options()
    # إعدادات لزيادة الاستقرار ومنع الـ Timeout في GitHub Actions
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-extensions")
    options.add_argument("--window-size=1920,1080")
    
    # تحسين تشغيل المتصفح
    service = Service(ChromeDriverManager().install())
    driver = None

    try:
        print(f"[{time.strftime('%H:%M:%S')}] جاري تشغيل المتصفح...")
        driver = webdriver.Chrome(service=service, options=options)
        driver.set_page_load_timeout(90) # زيادة مهلة تحميل الصفحة لتجنب الخطأ السابق
        
        print(f"[{time.strftime('%H:%M:%S')}] الدخول لموقع أضاحي...")
        driver.get("https://adhahi.dz/register")
        
        wait = WebDriverWait(driver, 60) # مهلة كافية للانتظار
        
        # العثور على حقل اختيار الولاية والنقر عليه
        input_field = wait.until(EC.element_to_be_clickable((By.ID, "reg-wilaya")))
        driver.execute_script("arguments[0].click();", input_field)
        
        print("📡 انتظار تحميل القائمة المنسدلة...")
        time.sleep(10) # وقت إضافي لضمان تحميل جميع الولايات من السيرفر

        # البحث عن الولايات (نقوم بالبحث في جميع عناصر القائمة li)
        items = driver.find_elements(By.TAG_NAME, "li")
        
        if len(items) < 10:
            print("⚠️ لم يتم تحميل الولايات بشكل صحيح (ربما ضغط على الموقع).")
            return

        found_any = False
        for item in items:
            text = item.text.strip()
            if not text: continue
            
            for state in MY_STATES:
                if state in text:
                    found_any = True
                    # التحقق من وجود كلمة "متوفر" أو "disponible"
                    if "متوفر" in text or "disponible" in text.lower():
                        msg = f"📢 @everyone **عاجل: توفر الحجز في {text}!**\nاحجز الآن فوراً: https://adhahi.dz/register"
                        send_discord(msg)
                        print(f"✅ مبروك! وجدنا حجز في: {text}")
                        return 
                    else:
                        print(f"⏳ {text}: غير متاح حالياً.")

        if not found_any:
            print("ℹ️ القائمة موجودة ولكن الولايات المختارة غير موجودة فيها حالياً.")

    except Exception as e:
        print(f"❌ حدث خطأ تقني: {e}")
    finally:
        if driver:
            driver.quit()
            print("🚪 تم إغلاق المتصفح.")

if __name__ == "__main__":
    run_check()
