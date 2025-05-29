from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time
import subprocess

# ✅ Setup headless browser for GitHub Actions
options = webdriver.ChromeOptions()
options.add_argument("--headless=new")  # Use new headless mode for better rendering
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
driver = webdriver.Chrome(options=options)

try:
    url = "https://meteo.gov.lk/index.php?option=com_content&view=article&id=104&Itemid=311&lang=en"
    driver.get(url)
    wait = WebDriverWait(driver, 90)
    print("✅ Page opened")

    # 🔘 Click the "3 Hourly Data" button
    time.sleep(5)
    buttons = driver.find_elements(By.TAG_NAME, "button")
    found = False
    for btn in buttons:
        print("🔘 Button found:", btn.text)
        if "3 Hourly Data" in btn.text:
            driver.execute_script("arguments[0].scrollIntoView(true);", btn)
            time.sleep(1)
            btn.click()
            found = True
            print("✅ Clicked '3 Hourly Data'")
            break
    if not found:
        raise Exception("❌ '3 Hourly Data' button not found.")

    # ⏳ Wait until table has actual data
    print("⏳ Waiting for table to appear...")
    try:
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#tab-content table tbody tr")))
        table = driver.find_element(By.CSS_SELECTOR, "#tab-content table")
        driver.execute_script("arguments[0].scrollIntoView(true);", table)
        print("✅ Table found and ready")
    except:
        driver.save_screenshot("table_not_found.png")
        raise Exception("❌ Table not found. Screenshot saved as table_not_found.png")

    # 📥 Extract table data
    rows = table.find_elements(By.CSS_SELECTOR, "tbody tr")
    data = []
    for row in rows:
        cols = row.find_elements(By.TAG_NAME, "td")
        if cols:
            data.append([col.text.strip() for col in cols])

    # 💾 Save to CSV
    if data:
        headers = ["Station_ID", "Station_Name", "Report_Time", "Rainfall (mm)", "Temperature (°C)", "RH (%)"]
        df = pd.DataFrame(data, columns=headers)
        filename = f"3hourly_data_{int(time.time())}.csv"
        df.to_csv(filename, index=False)
        print(f"✅ CSV saved: {filename}")

        # 🔁 Git commit and push
        try:
            subprocess.run(["git", "config", "--global", "user.email", "actions@github.com"], check=True)
            subprocess.run(["git", "config", "--global", "user.name", "GitHub Actions"], check=True)
            subprocess.run(["git", "add", filename], check=True)
            subprocess.run(["git", "commit", "-m", f"Add dataset: {filename}"], check=True)
            subprocess.run(["git", "push"], check=True)
            print("✅ CSV committed and pushed to GitHub")
        except subprocess.CalledProcessError as e:
            print("❌ Git operation failed:", e)

    else:
        print("⚠️ Table found, but no data rows extracted.")

finally:
    driver.quit()
