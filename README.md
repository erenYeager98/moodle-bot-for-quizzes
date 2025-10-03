# Automated Quiz Solver with Gemini API + Web Scraping (selenium)

## Overview
This Python script automates solving multiple-choice quizzes on Moodle using the Gemini AI model and Selenium.  
It logs in to the Moodle site, scrapes each question and its options, uses Gemini to predict the correct answer, selects the answer in the browser, and saves a detailed log of all attempts in a JSON file (`quiz_log.json`).  


---

## Requirements

1. Python 3.10+  
2. Google Gemini API access and key  
3. Selenium:  
   ```bash
   pip install selenium
   ```

4. Chrome WebDriver compatible with your Chrome version
5. Google Generative AI Python package:

   ```bash
   pip install google-generativeai
   ```

---

## Setup

1. Clone the repo using
```bash
git clone https://github.com/erenYeager98/moodle-bot-for-quizzes
```
2. **Set your Google API key** in the script:

```python
GOOGLE_API_KEY = "YOUR_GOOGLE_API_KEY"
```

3. **Download ChromeDriver** and ensure it's in your system PATH or in the same folder as the script.
4. Install required Python packages (if not already installed):

```bash
pip install selenium google-generativeai
```

---

## Usage

Run the script from the terminal:

```bash
python quiz_solver.py <username> <password> <quiz_base_url> <total_questions>
```

* `username` — Your Moodle username
* `password` — Your Moodle password
* `quiz_base_url` — The URL of the quiz page with `{page}` as placeholder for page number. Example:

```
https://lms2.ai.saveetha.in/mod/quiz/review.php?attempt=0&cmid=0&page={}
```

* `total_questions` — Total number of quiz questions

Example:

```bash
python quiz_solver.py 22001234 iamnigga "https://lms2.ai.saveetha.in/mod/quiz/review.php?attempt=0&cmid=0&page={}" 10
```

---

---

## Notes

* The script is designed for multiple-choice questions with radio buttons.
* Gemini model responses are processed to pick a single integer index.
* If Gemini cannot provide a valid answer, the question will be skipped.
* Always verify your answers before submitting manually if needed.

---
