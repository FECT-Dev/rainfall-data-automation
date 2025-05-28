from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time
import subprocess

# Setup for GitHub Actions compatibility
options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
driver = webdriver.Chrome(options=options)

try:
    url = "https://meteo.gov.lk/index.php?option=com_content&view=article&id=104&Itemid=311&lang=en"
    driver.get(url)
    wait = WebDriverWait(driver, 90)
    print("✅ Page opened")

    # Click the "3 Hourly Data" button
    time.sleep(5)
    all_buttons = driver.find_elements(By.TAG_NAME, "button")
    for b in all_buttons:
        print("🔘 Button found:", b.text)
        if "3 Hourly Data" in b.text:
            driver.execute_script("arguments[0].scrollIntoView(true);", b)
            time.sleep(1)
            b.click()
            print("✅ Clicked '3 Hourly Data'")
            break
    else:
        raise Exception("❌ '3 Hourly Data' button not found.")

    # Wait and retry for table to load
    print("⏳ Waiting for table to appear...")
    table = None
    for _ in range(10):  # Retry up to 10 times (~30 seconds)
        try:
            table = driver.find_element(By.CSS_SELECTOR, "#tab-content table")
            if table.is_displayed():
                driver.execute_script("arguments[0].scrollIntoView(true);", table)
                print("✅ Table found and ready")
                break
        except:
            pass
        time.sleep(3)
    else:
        driver.save_screenshot("table_not_found.png")
        raise Exception("❌ Table not found. Screenshot saved as table_not_found.png")

    # Extract table rows
    rows = table.find_elements(By.CSS_SELECTOR, "tbody tr")
    data = []
    for row in rows:
        cols = row.find_elements(By.TAG_NAME, "td")
        if cols:
            data.append([col.text for col in cols])

    # Save to CSV
    if data:
        headers = ["Station_ID", "Station_Name", "Report_Time", "Rainfall (mm)", "Temperature (°C)", "RH (%)"]
        df = pd.DataFrame(data, columns=headers)
        filename = f"3hourly_data_{int(time.time())}.csv"
        df.to_csv(filename, index=False)
        print(f"✅ CSV saved: {filename}")

        # Git commit and push
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
        print("⚠️ Table was found, but no data rows extracted.")

finally:
    driver.quit()
