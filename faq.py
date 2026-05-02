import json

def load_faq():
    with open("data/faq.json", "r", encoding="utf-8") as f:
        return json.load(f)

FAQ_DATA = load_faq()


def find_faq_answer(user_text, history=None):
    user_text = user_text.lower()

    # 🔹 1. прямое совпадение
    for item in FAQ_DATA:
        if item["question"] in user_text:
            return item["answer"]

    # 🔹 2. через контекст
    if history:
        last_user_messages = [
            msg["content"].lower()
            for msg in history
            if msg["role"] == "user"
        ]

        if last_user_messages:
            last_message = last_user_messages[-1]

            for item in FAQ_DATA:
                if item["question"] in last_message:
                    return item["answer"]

    return None