import json
import requests
import time

def start_func():
    
    # === CONFIG ===
    INPUT_FILE = "quiz_questions.json"
    ENDPOINT = "http://10.110.87.206:8002/ask"  # <-- REPLACE with your real endpoint

    # === LOAD QUESTIONS ===
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        questions = json.load(f)

    # === FILL MISSING ANSWERS ===
    for q in questions:
        if q.get("answer") is not None:
            continue  # already filled

        # Format prompt as required by endpoint
        prompt = q["question"] + "\n" + "\n".join(
            [f"{i}. {opt}" for i, opt in enumerate(q["options"])]
        )

        try:
            response = requests.post(ENDPOINT, json={"question": prompt})
            response.raise_for_status()
            answer_index = int(response.json().get("answer", -1))

            if 0 <= answer_index < q["option_count"]:
                q["answer"] = answer_index
                print(f"✅ Page {q['page']}: Answer = {answer_index}")
            else:
                print(f"❌ Page {q['page']}: Invalid answer index: {answer_index}")
        except Exception as e:
            print(f"⚠️ Page {q['page']}: Error contacting AI model: {e}")
            continue

        time.sleep(0.2)  # Optional: throttle requests to avoid overload

    # === SAVE BACK TO FILE ===
    with open(INPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(questions, f, indent=2, ensure_ascii=False)

    print("📁 Updated answers written to quiz_questions.json")
        
start_func()