def enrich_query(user_text, history):
    user_text = user_text.lower()

    # если короткий вопрос — добавляем контекст
    if len(user_text.split()) <= 3 and history:
        last_user_messages = [
            msg["content"]
            for msg in history
            if msg["role"] == "user"
        ]

        if last_user_messages:
            last_message = last_user_messages[-1]
            return f"{user_text} (в контексте: {last_message})"

    return user_text