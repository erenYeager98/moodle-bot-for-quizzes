import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By

def start_func(url):
    
    # === CONFIGURATION ===
    QUIZ_URL_BASE = url+"&page={}"
    LOGIN_URL = "https://lms2.ai.saveetha.in/login/index.php"
    USERNAME = "22003086"
    PASSWORD = "iamdk96"

    # === LOAD ANSWERS JSON ===
    with open("quiz_questions.json", "r", encoding="utf-8") as f:
        question_data = json.load(f)

    # === SETUP DRIVER ===
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(options=options)

    try:
        # === LOGIN ===
        driver.get(LOGIN_URL)
        time.sleep(2)
        driver.find_element(By.ID, "username").send_keys(USERNAME)
        driver.find_element(By.ID, "password").send_keys(PASSWORD)
        driver.find_element(By.ID, "loginbtn").click()
        time.sleep(3)

        # === ITERATE AND SUBMIT ANSWERS ===
        for entry in question_data:
            page = entry["page"]
            answer_index = entry["answer"]

            print(f"\n➡️ Page {page}: ", end="")

            if answer_index is None:
                print("⛔ No answer provided. Skipping.")
                continue

            driver.get(QUIZ_URL_BASE.format(page))
            time.sleep(2)

            try:
                options = driver.find_elements(By.CSS_SELECTOR, "input[type='radio']")
                if answer_index < len(options):
                    options[answer_index].click()
                    print(f"✅ Selected option {answer_index}")
                else:
                    print("❌ Invalid answer index. Skipping.")
                    continue
            except Exception as e:
                print(f"❌ Failed to select option: {e}")
                continue

            # Submit by clicking "Next"
            try:
                next_btn = driver.find_element(By.NAME, "next")
                next_btn.click()
                print("➡️ Submitted and moved to next page.")
            except Exception as e:
                print(f"❌ Failed to click 'Next': {e}")

    finally:
        print("\n✅ Submission script complete.")
        
start_func("https://lms2.ai.saveetha.in/mod/quiz/attempt.php?attempt=867231&cmid=40958")