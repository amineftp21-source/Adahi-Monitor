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
    except:
        pass

def run_monitor():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    
    # تحسين الأداء ومنع الصور لتسريع التحميل وتجنب الـ Renderer Timeout
    options.add_argument("--blink-settings=imagesEnabled=false")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

    driver = None
    try:
        print(f"[{time.strftime('%H:%M:%S')}] بدء المحاولة...")
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        
        # مهلة انتظار منطقية (45 ثانية) مع استراتيجية تحميل عادية
        driver.set_page_load_timeout(45)
        
        print(f"[{time.strftime('%H:%M:%S')}] الدخول للموقع...")
        driver.get(TARGET_URL)
        
        # انتظار ذكي حتى يظهر العنصر تماماً
        wait = WebDriverWait(driver, 50)
        
        print("🔍 البحث عن حقل الولايات...")
        # سننتظر وجود العنصر في الـ DOM أولاً
        input_field = wait.until(EC.presence_of_element_located((By.ID, "reg-wilaya")))
        
        # التمرير إليه لضمان أنه مرئي للمتصفح
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", input_field)
        time.sleep(3)
        
        # النقر باستخدام JavaScript (أكثر موثوقية في السيرفرات)
        driver.execute_script("arguments[0].click();", input_field)
        
        print("📡 فحص القائمة المنسدلة...")
        time.sleep(12) # وقت كافٍ للسيرفر ليرسل الولايات

        # البحث عن العناصر li باستخدام الطريقة العامة (أضمن من XPath المعقد)
        items = driver.find_elements(By.TAG_NAME, "li")
        
        if not items:
            print("⚠️ القائمة مفتوحة لكن لم يتم العثور على ولايات (ربما بطء في التحميل).")
            return

        print(f"✅ تم العثور على {len(items)} عنصر.")
        
        for item in items:
            text = item.text.strip()
            if any(state in text for state in MY_STATES):
                if "متوفر" in text or "disponible" in text.lower():
                    msg = f"📢 @everyone **عاجل: توفر الحجز في {text}!**\n{TARGET_URL}"
                    send_discord_msg(msg)
                    print(f"✅ تم الإرسال لديسكورد: {text}")
                    return 
                else:
                    print(f"⏳ {text}: غير متاح.")

    except Exception as e:
        # طباعة تفاصيل الخطأ بدقة لنعرف أين توقف بالضبط
        print(f"❌ خطأ في المرحلة: {type(e).__name__}")
        print(f"📝 التفاصيل: {str(e)[:150]}")
    finally:
        if driver:
            driver.quit()
            print("🚪 تم إغلاق المتصفح.")

if __name__ == "__main__":
    run_monitor()
