import json, time
from selenium import webdriver
from selenium.webdriver.common.by import By

# === CONFIG ===
LOGIN_URL = "https://lms2.ai.saveetha.in/login/index.php"
QUIZ_URL_BASE = "https://lms2.ai.saveetha.in/mod/quiz/attempt.php?attempt=832153&cmid=39988&page={}"
USERNAME = "22003086"
PASSWORD = "iamdk96"
TOTAL_PAGES = 50

# === SETUP DRIVER ===
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
driver = webdriver.Chrome(options=options)

question_data = []

try:
    # === LOGIN ===
    driver.get(LOGIN_URL)
    time.sleep(2)
    driver.find_element(By.ID, "username").send_keys(USERNAME)
    driver.find_element(By.ID, "password").send_keys(PASSWORD)
    driver.find_element(By.ID, "loginbtn").click()
    time.sleep(3)

    # === SCRAPE QUESTIONS ===
    for page in range(TOTAL_PAGES):
        driver.get(QUIZ_URL_BASE.format(page))
        time.sleep(1.5)

        try:
            qtext = driver.find_element(By.CLASS_NAME, "qtext").text.strip()

            # Extract options text using nearby label or div
            options = []
            answer_blocks = driver.find_elements(By.CSS_SELECTOR, ".answer > div")
            for block in answer_blocks:
                try:
                    label = block.find_element(By.CSS_SELECTOR, "div.flex-fill")
                    options.append(label.text.strip())
                except:
                    options.append(block.text.strip())

            question_data.append({
                "page": page,
                "question": qtext,
                "options": options,
                "option_count": len(options),
                "answer": None
            })

            print(f"✅ Page {page} captured: {qtext[:60]}...")

        except Exception as e:
            print(f"⚠️ Failed on page {page}: {e}")
            continue

finally:
    driver.quit()

# === SAVE TO FILE ===
with open("quiz_questions.json", "w", encoding="utf-8") as f:
    json.dump(question_data, f, indent=2, ensure_ascii=False)

print("📁 Saved to quiz_questions.json")
