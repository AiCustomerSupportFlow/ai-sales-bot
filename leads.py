from datetime import datetime

def save_lead(user_id, text):
    with open("leads.txt", "a", encoding="utf-8") as f:
        f.write(
            f"{datetime.now()} | user_id: {user_id} | {text}\n"
        )