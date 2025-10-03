import json
import time
import re
import os
import argparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

import google.generativeai as genai
from google.generativeai.types import GenerationConfig, HarmCategory, HarmBlockThreshold

LOGIN_URL = "https://lms2.ai.saveetha.in/login/index.php"

try:
    GOOGLE_API_KEY = "your api key here"
except KeyError:
    print("api key kaasu kuduthu vaangunga brother.")
    exit()

MODEL_NAME = "gemini-2.5-flash"
LOG_FILE = "quiz_log.json"


def safe_get_response_text(response):
    if not response.candidates:
        return None

    for c in response.candidates:
        if not c.content.parts:
            continue
        text_parts = [p.text for p in c.content.parts if hasattr(p, "text")]
        if text_parts:
            return " ".join(text_parts).strip()
    return None


def get_gemini_answer(model, generation_config, question_text, options_list):
    prompt = question_text + "\n" + "\n".join(
        [f"{i}. {opt}" for i, opt in enumerate(options_list)]
    )

    safety_settings = {
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
    }

    try:
        response = model.generate_content(
            prompt,
            generation_config=generation_config,
            safety_settings=safety_settings
        )

        model_answer_text = safe_get_response_text(response)

        if not model_answer_text:
            print("Gemini returned no usable output.")
            return None

        match = re.search(r'\d+', model_answer_text)
        if match:
            answer_index = int(match.group(0))
            if 0 <= answer_index < len(options_list):
                print(f"Gemini chose index: {answer_index} ('{model_answer_text}')")
                return answer_index
            else:
                print(f"Gemini returned out-of-range index: {answer_index}")
                return None
        else:
            print(f"Gemini response unclear: '{model_answer_text}'")
            return None

    except Exception as e:
        print(f"Error contacting Gemini API: {e}")
        return None


def solve_quiz_realtime(username, password, base_url, total_questions):
    print("Configuring Gemini API client...")
    genai.configure(api_key=GOOGLE_API_KEY)

    system_instruction = (
        "You are an expert quiz solver. Your task is to identify the correct option for the given multiple-choice question. "
        "Read the question and the options carefully. "
        "Your response MUST be a single integer representing the index of the correct option (starting from 0). "
        "Do NOT provide any explanation, preamble, or any other text. Just the number."
    )
    model = genai.GenerativeModel(MODEL_NAME, system_instruction=system_instruction)
    generation_config = GenerationConfig(temperature=0.0, top_p=0.1, max_output_tokens=1000)

    print("Setting up web driver...")
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(options=options)

    completed_questions = []

    try:
        print(f"Logging in as {username}...")
        driver.get(LOGIN_URL)
        time.sleep(1)
        driver.find_element(By.ID, "username").send_keys(username)
        driver.find_element(By.ID, "password").send_keys(password)
        driver.find_element(By.ID, "loginbtn").click()
        time.sleep(2)
        print("Login successful.")

        for page in range(total_questions):
            print("-" * 50)
            print(f"Processing page {page + 1}/{total_questions}...")

            driver.get(base_url.format(page))
            time.sleep(1.5)

            try:
                qtext = driver.find_element(By.CLASS_NAME, "qtext").text.strip()

                options_text = []
                answer_blocks = driver.find_elements(By.CSS_SELECTOR, ".answer > div")
                for block in answer_blocks:
                    options_text.append(block.find_element(By.CSS_SELECTOR, "div.flex-fill").text.strip())

                print(f"Scraped question: {qtext[:70]}...")

                answer_index = get_gemini_answer(model, generation_config, qtext, options_text)

                completed_questions.append({
                    "page": page, "question": qtext, "options": options_text,
                    "submitted_answer_index": answer_index
                })

                if answer_index is None:
                    print("No valid answer from Gemini. Skipping...")
                else:
                    radio_buttons = driver.find_elements(By.CSS_SELECTOR, "input[type='radio']")
                    if answer_index < len(radio_buttons):
                        radio_buttons[answer_index].click()
                        print(f"Selected option {answer_index}.")
                    else:
                        print("Radio button for the answer index not found. Skipping.")

                time.sleep(0.5)

                if page < total_questions - 1:
                    driver.find_element(By.NAME, "next").click()
                    print("Clicked 'Next page'.")
                else:
                    print("Last question. Looking for 'Finish attempt...' button.")
                    try:
                        driver.find_element(By.CSS_SELECTOR, "input.mod_quiz-next-nav[value='Finish attempt...']").click()
                        print("Clicked 'Finish attempt...'.")
                    except NoSuchElementException:
                        print("Could not find 'Finish attempt...' button. Manual submission may be required.")

            except Exception as e:
                print(f"Error on page {page}: {e}")
                completed_questions.append({"page": page, "error": str(e)})
                continue

    finally:
        print("-" * 50)
        print("Quiz finished or an error occurred. Closing browser.")
        driver.quit()

        with open(LOG_FILE, "w", encoding="utf-8") as f:
            json.dump(completed_questions, f, indent=2, ensure_ascii=False)
        print(f"Full log saved to {LOG_FILE}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Automated quiz solver with Gemini + Selenium")
    parser.add_argument("username", type=str, help="Moodle username")
    parser.add_argument("password", type=str, help="Moodle password")
    parser.add_argument("quiz_base_url", type=str, help="Quiz base URL with {page} placeholder")
    parser.add_argument("total_questions", type=int, help="Total number of quiz questions")

    args = parser.parse_args()

    solve_quiz_realtime(args.username, args.password, args.quiz_base_url, args.total_questions)