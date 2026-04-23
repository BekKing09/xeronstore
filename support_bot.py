import os
import django
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from dotenv import load_dotenv

# 1. Muhitni yuklash
load_dotenv()

# 2. Django sozlamalari
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings') 
django.setup()

# 3. .env dan ma'lumotlarni olish
API_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# --- HOLATLAR (STATES) ---
class PaymentSteps(StatesGroup):
    waiting_for_uid = State()
    waiting_for_photo = State()

class SupportSteps(StatesGroup):
    waiting_for_text = State()

# --- TUGMALAR ---
def get_main_menu():
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="💰 Hisobni to'ldirish")],
        [KeyboardButton(text="💡 Takliflar"), KeyboardButton(text="⚠️ Shikoyat")],
        [KeyboardButton(text="👨‍💻 Admin bilan bog'lanish")]
    ], resize_keyboard=True)

# Maxsus belgilarni tozalash (HTML xato bermasligi uchun)
def escape_html(text):
    return str(text).replace('<', '&lt;').replace('>', '&gt;').replace('&', '&amp;')

@dp.message(Command("start"))
async def start_cmd(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        f"👋 <b>Assalomu alaykum, {escape_html(message.from_user.full_name)}!</b>\n\n"
        "🚀 <b>XERON SHOP</b> rasmiy qo'llab-quvvatlash tizimiga xush kelibsiz.\n"
        "Sizga qanday yordam bera olamiz? Quyidagi menyudan foydalaning:",
        reply_markup=get_main_menu(),
        parse_mode="HTML"
    )

# --- HISOB TO'LDIRISH ---
@dp.message(F.text == "💰 Hisobni to'ldirish")
async def start_payment(message: types.Message, state: FSMContext):
    await state.set_state(PaymentSteps.waiting_for_uid)
    await message.answer(
        "🆔 <b>1-bosqich: UID raqamingizni kiriting</b>\n\n"
        "Iltimos, saytdagi profilingizda ko'rsatilgan <b>7 xonali UID</b> raqamingizni yuboring.\n"
        "<i>(Masalan: 1002345)</i>",
        reply_markup=ReplyKeyboardRemove(),
        parse_mode="HTML"
    )

@dp.message(PaymentSteps.waiting_for_uid)
async def process_uid(message: types.Message, state: FSMContext):
    if not message.text or not message.text.isdigit():
        await message.answer("❌ <b>Xato!</b> Iltimos, faqat raqamlardan iborat bo'lgan UIDni kiriting.\nMasalan: <code>1002345</code>", parse_mode="HTML")
        return

    await state.update_data(user_uid=message.text)
    await state.set_state(PaymentSteps.waiting_for_photo)
    await message.answer(
        "📸 <b>2-bosqich: To'lov chekini yuboring</b>\n\n"
        "To'lov amalga oshirilganligi haqidagi skrinshotni yuboring.\n"
        "<i>(Iltimos, faqat rasm yuboring)</i>",
        parse_mode="HTML"
    )

@dp.message(PaymentSteps.waiting_for_photo, ~F.photo)
async def photo_validation(message: types.Message):
    await message.answer("❌ <b>Xato!</b> Iltimos, to'lov chekini <b>rasm (photo)</b> holatida yuboring.", parse_mode="HTML")

@dp.message(PaymentSteps.waiting_for_photo, F.photo)
async def process_photo(message: types.Message, state: FSMContext):
    data = await state.get_data()
    uid = data.get('user_uid')
    
    user_info = f"@{message.from_user.username}" if message.from_user.username else "Noma'lum"
    
    await bot.send_photo(
        ADMIN_ID,
        message.photo[-1].file_id,
        caption=(
            f"🔔 <b>YANGI TO'LOV SO'ROVI!</b>\n"
            f"━━━━━━━━━━━━━━━\n"
            f"👤 <b>User:</b> {escape_html(message.from_user.full_name)}\n"
            f"🔗 <b>Username:</b> {user_info}\n"
            f"🆔 <b>UID:</b> <code>{uid}</code>\n"
            f"📂 <b>TG ID:</b> <code>{message.from_user.id}</code>\n"
            f"━━━━━━━━━━━━━━━"
        ),
        parse_mode="HTML"
    )
    
    await state.clear()
    await message.answer(
        "✅ <b>Muvaffaqiyatli!</b>\n\n"
        "Sizning to'lov so'rovingiz adminga yetkazildi. ⏱ 5-15 daqiqa ichida tekshirilib, balansingiz to'ldiriladi.\n\n"
        "<b>XERON SHOP</b>ni tanlaganingiz uchun rahmat! 😊",
        reply_markup=get_main_menu(),
        parse_mode="HTML"
    )

# --- TAKLIF VA SHIKOYATLAR ---
@dp.message(F.text.in_(["💡 Takliflar", "⚠️ Shikoyat", "👨‍💻 Admin bilan bog'lanish"]))
async def support_start(message: types.Message, state: FSMContext):
    await state.set_state(SupportSteps.waiting_for_text)
    await state.update_data(support_type=message.text)
    
    prompts = {
        "💡 Takliflar": "✍️ <b>Saytimizni yaxshilash bo'yicha taklifingizni yozing:</b>",
        "⚠️ Shikoyat": "🛠 <b>Qanday muammoga duch keldingiz? Batafsil tushuntirib bering:</b>",
        "👨‍💻 Admin bilan bog'lanish": "👨‍💻 <b>Admin uchun xabaringizni qoldiring:</b>"
    }
    
    await message.answer(prompts.get(message.text), reply_markup=ReplyKeyboardRemove(), parse_mode="HTML")

@dp.message(SupportSteps.waiting_for_text)
async def support_finish(message: types.Message, state: FSMContext):
    data = await state.get_data()
    s_type = data.get('support_type')
    
    user_info = f"@{message.from_user.username}" if message.from_user.username else "Noma'lum"

    await bot.send_message(
        ADMIN_ID,
        f"📩 <b>YANGI MUROJAAT ({s_type})</b>\n"
        f"━━━━━━━━━━━━━━━\n"
        f"👤 <b>User:</b> {escape_html(message.from_user.full_name)}\n"
        f"🔗 <b>Username:</b> {user_info}\n"
        f"📝 <b>Matn:</b> {escape_html(message.text)}\n"
        f"━━━━━━━━━━━━━━━",
        parse_mode="HTML"
    )
    
    await state.clear()
    
    if s_type == "💡 Takliflar":
        response_text = (
            "✅ <b>Taklifingiz qabul qilindi!</b>\n\n"
            "XERON SHOP jamoasi sizning g'oyangizni albatta ko'rib chiqadi. "
            "Biz foydalanuvchilarimizning fikrlarini qadrlaymiz. "
            "Agar taklifingiz loyihamizga mos kelsa, uni tez orada joriy etamiz! ✨"
        )
    elif s_type == "⚠️ Shikoyat":
        response_text = (
            "✅ <b>Shikoyatingiz yuborildi.</b>\n\n"
            "Yuzaga kelgan noqulaylik uchun uzr so'raymiz. 🛠\n"
            "Mutaxassislarimiz muammoni imkon qadar tezroq o'rganib chiqishadi "
            "va uni bartaraf etish choralarini ko'rishadi."
        )
    else:
        response_text = (
            "✅ <b>Xabaringiz adminga yetkazildi.</b>\n\n"
            "Operatorlarimiz bo'shashi bilan sizga javob berishadi. "
            "Iltimos, biroz kutishingizni so'raymiz. 👨‍💻"
        )
    
    await message.answer(response_text, reply_markup=get_main_menu(), parse_mode="HTML")

@dp.message()
async def echo_all(message: types.Message):
    await message.answer("⚠️ <b>Noma'lum buyruq.</b>\nIltimos, menyu tugmalaridan foydalaning:", reply_markup=get_main_menu(), parse_mode="HTML")

async def main():
    print("Bot HTML rejimida ishga tushdi...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())