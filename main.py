import time
import crawl_questions
import update_answers
import submit_answers

_url = input("Enter the quiz URL:")
_questions = int(input("Enter the number of questions:"))
print(" Step 1: Crawling quiz questions using Selenium...")
try:
    crawl_questions.start_func(_url,_questions)
    print("Step 1 complete: quiz_questions.json updated.")
except Exception as e:
    print(" Step 1 failed:", e)
    exit(1)

time.sleep(1)

print("\n Step 2: Updating answers using AI model endpoint...")
try:
    update_answers.start_func()
    print(" Step 2 complete: Answers filled in JSON.")
except Exception as e:
    print(" Step 2 failed:", e)
    exit(1)

time.sleep(1)

print("\n Step 3: Submitting answers via Selenium...")
print(" Browser will stay open after this step for inspection.")
try:
    submit_answers.start_func(_url)
    print(" Step 3 complete: All answers submitted.")
except Exception as e:
    print("Step 3 failed:", e)
    exit(1)

print("\n All steps completed successfully!")
