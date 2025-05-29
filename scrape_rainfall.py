from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time
import subprocess
import os

# ✅ Headless browser setup (for GitHub Actions)
options = webdriver.ChromeOptions()
options.add_argument("--headless=new")  # New headless mode for better rendering
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
driver = webdriver.Chrome(options=options)

try:
    url = "https://meteo.gov.lk/index.php?option=com_content&view=article&id=104&Itemid=311&lang=en"
    driver.get(url)
    print("✅ Page opened")

    # 🔘 Click "3 Hourly Data" button
    time.sleep(5)
    buttons = driver.find_elements(By.TAG_NAME, "button")
    for btn in buttons:
        print("🔘 Button found:", btn.text)
        if "3 Hourly Data" in btn.text:
            driver.execute_script("arguments[0].scrollIntoView(true);", btn)
            time.sleep(1)
            btn.click()
            print("✅ Clicked '3 Hourly Data'")
            break
    else:
        raise Exception("❌ '3 Hourly Data' button not found.")

    # ⏳ Retry loop for dynamic table content to load
    print("⏳ Waiting for table to load...")
    table = None
    rows = []
    for attempt in range(20):  # Retry up to ~60s
        try:
            container = driver.find_element(By.ID, "tab-content")
            table = container.find_element(By.TAG_NAME, "table")
            rows = table.find_elements(By.CSS_SELECTOR, "tbody tr")
            if len(rows) > 0:
                driver.execute_script("arguments[0].scrollIntoView(true);", table)
                print(f"✅ Table found with {len(rows)} rows")
                break
        except Exception:
            pass
        print(f"⏳ Retry {attempt + 1}/20...")
        time.sleep(3)
    else:
        with open("debug_page.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        driver.save_screenshot("table_not_found.png")
        print("❌ Table not found. Screenshot and HTML saved.")
        exit(0)  # Exit cleanly without error

    # 🗓 Extract table data
    data = []
    for row in rows:
        cols = row.find_elements(By.TAG_NAME, "td")
        if cols:
            data.append([col.text.strip() for col in cols])

    # 📆 Save data to CSV (even if empty)
    headers = ["Station_ID", "Station_Name", "Report_Time", "Rainfall (mm)", "Temperature (°C)", "RH (%)"]
    df = pd.DataFrame(data, columns=headers)
    filename = f"3hourly_data_{int(time.time())}.csv"
    df.to_csv(filename, index=False)
    print(f"📆 CSV saved: {filename} with {len(data)} rows")

    # 📌 Commit and push to GitHub
    try:
        subprocess.run(["git", "config", "--global", "user.email", "actions@github.com"], check=True)
        subprocess.run(["git", "config", "--global", "user.name", "GitHub Actions"], check=True)
        subprocess.run(["git", "add", filename], check=True)
        subprocess.run(["git", "commit", "-m", f"Add dataset: {filename}"], check=True)
        subprocess.run(["git", "push"], check=True)
        print("✅ CSV committed and pushed to GitHub")
    except subprocess.CalledProcessError as e:
        print("❌ Git operation failed:", e)

finally:
    driver.quit()
