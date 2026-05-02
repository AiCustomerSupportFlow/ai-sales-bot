def check_objection(user_text):
    text = user_text.lower()

    triggers = [
        "дорого",
        "дороговато",
        "дешевле",
        "дороже",
        "у конкурентов дешевле"
    ]

    for trigger in triggers:
        if trigger in text:
            return True

    return False


def handle_objection(user_text):
    return (
        "Понимаю, цена важна 🙂\n\n"
        "У нас доставка включает быстрые сроки (2–3 дня) и надёжность.\n"
        "Плюс, если товар не подойдёт — вы можете вернуть его в течение 14 дней.\n\n"
        "Если хотите, могу подобрать более бюджетный вариант 👍"
    )