import asyncio
import os
import requests
from faq import find_faq_answer
from objections import check_objection, handle_objection
from memory import get_history, save_message
from context import enrich_query
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from leads import save_lead
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram import F
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from dotenv import load_dotenv
from aiogram.filters import StateFilter
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import re
from google_sheets import save_to_sheet
import asyncio

class OrderState(StatesGroup):
    waiting_for_product = State()
    waiting_for_city = State()
    waiting_for_phone = State()

# Загружаем .env
load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

if not TELEGRAM_TOKEN:
    raise ValueError("Нет TELEGRAM_TOKEN в .env")

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

SYSTEM_PROMPT = """
Ты — AI-ассистент бизнеса.

Отвечай:
- кратко
- по делу
- дружелюбно

Если вопрос про покупку — помоги выбрать.
Если возражение — обработай мягко.
"""

async def follow_up(user_id):
    # через 1 день (86400 секунд)
    await asyncio.sleep(86400)

    await bot.send_message(
        user_id,
        "Привет! Вы оставляли заявку 🙂\n"
        "Удалось оформить заказ или нужна помощь?"
    )

    # через ещё 2 дня
    await asyncio.sleep(2 * 86400)

    await bot.send_message(
        user_id,
        "Могу предложить выгодный вариант или скидку 👍\n"
        "Хотите посмотреть?"
    )

def get_main_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛒 Купить", callback_data="buy")],
        [InlineKeyboardButton(text="❓ Задать вопрос", callback_data="ask")],
        [InlineKeyboardButton(text="👨‍💻 Менеджер", callback_data="manager")]
    ])
    return keyboard

# 🔥 Функция запроса к Ollama
def ask_ollama(user_text, history):
    url = "http://localhost:11434/api/generate"

    history_text = ""

    for msg in history:
        if msg["role"] == "user":
            history_text += f"Пользователь: {msg['content']}\n"
        else:
            history_text += f"Бот: {msg['content']}\n"

    prompt = f"""
{SYSTEM_PROMPT}

История диалога:
{history_text}

Пользователь: {user_text}
Ответ:
"""

    response = requests.post(url, json={
        "model": "mistral",
        "prompt": prompt,
        "stream": False
    })

    if response.status_code != 200:
        return "Ошибка связи с AI"

    data = response.json()

    return data.get("response", "Нет ответа")

# /start
@dp.message(CommandStart())
async def start(message: types.Message):
    await message.answer(
    "Привет! Я AI-ассистент. Чем помочь?",
    reply_markup=get_main_keyboard()
)


# любое сообщение
@dp.message(StateFilter(None))
#async def handle_message(message: types.Message):
async def handle_message(message: types.Message, state: FSMContext):
    user_text = message.text
    user_id = message.from_user.id
    history = get_history(user_id)
    buy_triggers = ["хочу купить", "заказать", "беру", "оформить"]
    
    
    # 🔹 4. если пользователь хочет купить
   

   # if user_text.lower().strip() in buy_triggers:
        
      #  save_lead(user_id, user_text)
      #  
      #  await bot.send_message(
       #     ADMIN_ID,
      #      f"🔥 Новый лид!\n\nUser ID: {user_id}\nСообщение: {user_text}"
       # )
        
    #    answer = (
         #   "Отлично! 👍 Давайте оформим заказ.\n\n"
         #   "Напишите, пожалуйста:\n"
         #   "1. Какой товар\n"
           # "2. Город доставки\n"
           # "3. Контактный номер\n\n"
            #"Я передам менеджеру 👌"
        #)

        #save_message(user_id, "user", user_text)
        #save_message(user_id, "assistant", answer)
    

        #await message.answer(faq_answer, reply_markup=get_main_keyboard())
        #await message.answer(answer, reply_markup=get_main_keyboard())
        #return
    
    if user_text.lower().strip() in buy_triggers:
        await state.set_state(OrderState.waiting_for_product)

        await message.answer(
            "Отлично! 👍\n\nКакой товар вас интересует?"
        )
        return

    # 🔹 1. Проверка FAQ (обычная)
    faq_answer = find_faq_answer(user_text, history)
    if faq_answer:
        save_message(user_id, "user", user_text)
        save_message(user_id, "assistant", faq_answer)

        #await message.answer(faq_answer, reply_markup=get_main_keyboard())
        await message.answer(answer, reply_markup=get_main_keyboard())
        return

    # 🔹 2. Проверка возражения
    if check_objection(user_text):
        answer = handle_objection(user_text)

        save_message(user_id, "user", user_text)
        save_message(user_id, "assistant", answer)

        #await message.answer(faq_answer, reply_markup=get_main_keyboard())
        await message.answer(answer, reply_markup=get_main_keyboard())
        return

    # 🔹 3. защита от коротких вопросов (контекст)
    if len(user_text.split()) <= 3 and history:
        last_user = None

        for msg in reversed(history):
            if msg["role"] == "user":
                last_user = msg["content"]
                break

        if last_user:
            combined = f"{last_user} {user_text}"

            faq_answer = find_faq_answer(combined, history)
            if faq_answer:
                save_message(user_id, "user", user_text)
                save_message(user_id, "assistant", faq_answer)

                #await message.answer(faq_answer, reply_markup=get_main_keyboard())
                await message.answer(answer, reply_markup=get_main_keyboard())
                return
            

   


    # 🔹 4. AI ответ
    enhanced_text = enrich_query(user_text, history)
    answer = ask_ollama(enhanced_text, history)

    save_message(user_id, "user", user_text)
    save_message(user_id, "assistant", answer)

    
    #await message.answer(faq_answer, reply_markup=get_main_keyboard())
    await message.answer(answer, reply_markup=get_main_keyboard())
    return


@dp.callback_query()
async def handle_buttons(callback: types.CallbackQuery):
    data = callback.data

    if data == "buy":
        await callback.message.answer(
            "Отлично! 👍 Напишите:\n"
            "1. Какой товар\n"
            "2. Город\n"
            "3. Телефон"
        )

    elif data == "ask":
        await callback.message.answer(
            "Задайте ваш вопрос, я помогу 🙂"
        )

    elif data == "manager":
        await callback.message.answer(
            "Передаю вас менеджеру 👨‍💻\n"
            "Он свяжется с вами в ближайшее время."
        )

    await callback.answer()
    
@dp.message(OrderState.waiting_for_product)
async def get_product(message: types.Message, state: FSMContext):
    await state.update_data(product=message.text)

    await state.set_state(OrderState.waiting_for_city)

    await message.answer("Укажите город доставки:")
    
@dp.message(OrderState.waiting_for_city)
async def get_city(message: types.Message, state: FSMContext):
    await state.update_data(city=message.text)

    await state.set_state(OrderState.waiting_for_phone)

    await message.answer(
        "Нажмите кнопку ниже, чтобы отправить номер 📱",
        reply_markup=get_phone_keyboard()
    )
    

    
def get_phone_keyboard():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📱 Отправить номер", request_contact=True)]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    return keyboard

@dp.message(OrderState.waiting_for_phone)
async def get_phone(message: types.Message, state: FSMContext):
    data = await state.get_data()

    product = data.get("product")
    city = data.get("city")

    phone = None

    # 📱 если нажали кнопку
    if message.contact:
        phone = message.contact.phone_number

    # ✍️ если написали текстом
    elif message.text:
        import re
        match = re.search(r"\+?\d[\d\s\-\(\)]{8,}", message.text)
        if match:
            phone = match.group()

    # ❌ если ничего не нашли
    if not phone:
        await message.answer("Введите корректный номер или нажмите кнопку 📱")
        return

    user_id = message.from_user.id

    from leads import save_lead
    save_lead(user_id, f"{product} | {city} | {phone}")
    save_to_sheet(user_id, product, city, phone)

    await bot.send_message(
        ADMIN_ID,
        f"🔥 Новый заказ!\n\n"
        f"Товар: {product}\n"
        f"Город: {city}\n"
        f"Телефон: {phone}\n"
        f"User ID: {user_id}"
    )

    await message.answer(
        "Спасибо! 🙌\nМенеджер скоро свяжется с вами.",
        reply_markup=get_main_keyboard()
    )

    await state.clear()
    asyncio.create_task(follow_up(user_id))
# запуск
async def main():
    print("Бот с Ollama запущен...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())