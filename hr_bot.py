import logging
import asyncio
import html
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.keyboard import ReplyKeyboardBuilder

# --- НАЛАШТУВАННЯ БОТА ---
BOT_TOKEN = "8962706217:AAGSCQ4f3Vg4BhBqW-ccY5SZb8unFu-i9F8" 
HR_CHAT_ID = -1003753845122  

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Стан для анкетування кандидата (додано номер телефону)
class Form(StatesGroup):
    name = State()
    age = State()
    experience = State()
    phone = State()

def get_main_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.button(text="📋 Переглянути вакансію")
    builder.button(text="✍️ Заповнити анкету")
    builder.button(text="💬 Зв'язатися з HR")
    builder.adjust(1)
    return builder.as_markup(resize_keyboard=True)

def get_hr_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.button(text="📞 Співбесіда в телефонному режимі")
    builder.button(text="⌨️ Співбесіда в текстовому режимі")
    builder.button(text="⬅️ Назад")
    builder.adjust(1)
    return builder.as_markup(resize_keyboard=True)

@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Вітаємо! Цей бот допоможе вам ознайомитися з вакансією та подати заявку в нашу команду.",
        reply_markup=get_main_keyboard()
    )

@dp.message(lambda message: message.text == "📋 Переглянути вакансію")
async def show_vacancy(message: types.Message):
    text = (
        "✨ <b>Вакансія: Помічник парапсихолога</b>\n\n"
        "📌 <b>Обов'язки:</b>\n"
        "— обробка вхідних дзвінків;\n"
        "— консультація клієнтів по телефону;\n"
        "— запис до спеціаліста.\n\n"
        "💰 <b>Умови:</b>\n"
        "— Графік 5/2 з 09:00 до 19:00;\n"
        "— Мінімальна ставка 36 000 грн;\n"
        "— Підвищена ставка 52 000 грн за перевиконання плану;\n"
        "— Бонусна система;\n"
        "— Регулярні виплати кожного тижня."
    )
    await message.answer(text, parse_mode="HTML")

@dp.message(lambda message: message.text == "💬 Зв'язатися з HR")
async def contact_hr_options(message: types.Message):
    await message.answer("Оберіть зручний формат для проведення співбесіди:", reply_markup=get_hr_keyboard())

# Режими зв'язку (текстовий / телефонний)
@dp.message(lambda message: message.text in ["📞 Співбесіда в телефонному режимі", "⌨️ Співбесіда в текстовому режимі"])
async def hr_format_selection(message: types.Message):
    raw_name = message.from_user.full_name if message.from_user.full_name else "Кандидат"
    user_name = html.escape(raw_name)
    
    if message.from_user.username:
        username = f"@{html.escape(message.from_user.username)}"
    else:
        username = "Не вказано"
    
    hr_alert = (
        "🔔 <b>Обрано формат співбесіди!</b>\n\n"
        f"👤 <b>Кандидат:</b> {user_name}\n"
        f"⚙️ <b>Обраний варіант:</b> {html.escape(message.text)}\n"
        f"💬 <b>Telegram:</b> {username}\n"
        f"🔗 <a href='tg://user?id={message.from_user.id}'>Відкрити чат з кандидатом</a>"
    )
    
    try:
        await bot.send_message(chat_id=HR_CHAT_ID, text=hr_alert, parse_mode="HTML")
    except Exception as e:
        print(f"Помилка надсилання вибору формату: {e}")

    # Зміна тексту відповіді кандидату залежно від обраного типу
    if message.text == "⌨️ Співбесіда в текстовому режимі":
        await message.answer(
            "Ця інформація вже дійшла до HR менеджера та скоро він вам напише.", 
            reply_markup=get_main_keyboard()
        )
    else:
        await message.answer(
            "Ця інформація вже дійшла до HR менеджера та скоро він вам зателефонує.", 
            reply_markup=get_main_keyboard()
        )

@dp.message(lambda message: message.text == "⬅️ Назад")
async def go_back(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Ви повернулися в головне меню", reply_markup=get_main_keyboard())

# --- АНКЕТУВАННЯ ---
@dp.message(lambda message: message.text == "✍️ Заповнити анкету")
async def start_form(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Будь ласка, вкажіть ваше <b>Ім'я та Прізвище</b>:", parse_mode="HTML")
    await state.set_state(Form.name)

@dp.message(Form.name)
async def process_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Вкажіть ваш <b>вік</b>:", parse_mode="HTML")
    await state.set_state(Form.age)

@dp.message(Form.age)
async def process_age(message: types.Message, state: FSMContext):
    await state.update_data(age=message.text)
    await message.answer("Чи був у вас <b>досвід у подібній сфері</b>? (Опишіть коротко або напишіть 'ні'):", parse_mode="HTML")
    await state.set_state(Form.experience)

@dp.message(Form.experience)
async def process_experience(message: types.Message, state: FSMContext):
    await state.update_data(experience=message.text)
    await message.answer("Будь ласка, вкажіть ваш <b>актуальний номер телефону</b>, за яким можна зв'язатись:", parse_mode="HTML")
    await state.set_state(Form.phone)

@dp.message(Form.phone)
async def process_phone(message: types.Message, state: FSMContext):
    await state.update_data(phone=message.text)
    user_data = await state.get_data()
    await state.clear() 

    # Безпечне кодування тексту
    cand_name = html.escape(user_data.get('name', message.from_user.full_name or "Кандидат"))
    cand_age = html.escape(user_data.get('age', 'Не вказано'))
    cand_exp = html.escape(user_data.get('experience', 'Не вказано'))
    cand_phone = html.escape(user_data.get('phone', 'Не вказано'))
    
    if message.from_user.username:
        username = f"@{html.escape(message.from_user.username)}"
    else:
        username = "Не вказано"

    hr_message = (
        "🚨 <b>Нова анкетна заявка!</b>\n\n"
        "💼 <b>Вакансія:</b> Помічник парапсихолога\n"
        f"👤 <b>Ім'я:</b> {cand_name}\n"
        f"🎂 <b>Вік:</b> {cand_age}\n"
        f"📞 <b>Телефон:</b> {cand_phone}\n"
        f"🔮 <b>Досвід у подібній сфері:</b> {cand_exp}\n\n"
        f"💬 <b>Telegram:</b> {username}\n"
        f"🔗 <a href='tg://user?id={message.from_user.id}'>Відкрити чат з кандидатом</a>"
    )

    try:
        await bot.send_message(chat_id=HR_CHAT_ID, text=hr_message, parse_mode="HTML")
        await message.answer(
            "дуже дякуємо за звернення, найближчим часом наш HR менеджер зв'яжеться з Вами, очікуйте",
            reply_markup=get_main_keyboard()
        )
    except Exception as e:
        await message.answer(
            "Сталася помилка при відправці анкет. Спробуйте пізніше.",
            reply_markup=get_main_keyboard()
        )
        print(f"Помилка відправки анкети: {e}")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())