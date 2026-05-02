# простая память в оперативке (MVP)

user_memory = {}


def get_history(user_id):
    return user_memory.get(user_id, [])


def save_message(user_id, role, text):
    if user_id not in user_memory:
        user_memory[user_id] = []

    user_memory[user_id].append({
        "role": role,
        "content": text
    })

    # ограничиваем память (последние 10 сообщений)
    user_memory[user_id] = user_memory[user_id][-10:]