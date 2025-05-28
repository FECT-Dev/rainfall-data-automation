from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time

options = webdriver.ChromeOptions()
# options.add_argument("--headless")  # Keep visible for debugging
driver = webdriver.Chrome(options=options)

try:
    # Go directly to the 3 Hourly Data page
    url = "https://meteo.gov.lk/index.php?option=com_content&view=article&id=104&Itemid=311&lang=en"
    driver.get(url)
    wait = WebDriverWait(driver, 30)
    print("✅ Page opened")

    # ✅ Click the "Load Data" button
    load_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Load Data')]")))
    load_btn.click()
    print("✅ Clicked 'Load Data' button")

    # ✅ Wait for the table data to load
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#tab-content table tbody tr td")))
    print("✅ Table data detected")

    # Scrape the table
    table = driver.find_element(By.CSS_SELECTOR, "#tab-content table")
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
    else:
        print("⚠️ No data rows found.")

finally:
    driver.quit()
