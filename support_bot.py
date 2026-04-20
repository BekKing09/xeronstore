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

@dp.message(Command("start"))
async def start_cmd(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        f"👋 **Assalomu alaykum, {message.from_user.full_name}!**\n\n"
        "🚀 **XERON SHOP** rasmiy qo'llab-quvvatlash tizimiga xush kelibsiz.\n"
        "Sizga qanday yordam bera olamiz? Quyidagi menyudan foydalaning:",
        reply_markup=get_main_menu(),
        parse_mode="Markdown"
    )

# --- HISOB TO'LDIRISH (VALIDATSIYA BILAN) ---
@dp.message(F.text == "💰 Hisobni to'ldirish")
async def start_payment(message: types.Message, state: FSMContext):
    await state.set_state(PaymentSteps.waiting_for_uid)
    await message.answer(
        "🆔 **1-bosqich: UID raqamingizni kiriting**\n\n"
        "Iltimos, saytdagi profilingizda ko'rsatilgan **7 xonali UID** raqamingizni yuboring.\n"
        "_(Faqat raqamlardan iborat bo'lishi kerak)_",
        reply_markup=ReplyKeyboardRemove(),
        parse_mode="Markdown"
    )

# UID ni tekshirish (Faqat raqam va matn bo'lishi shart)
@dp.message(PaymentSteps.waiting_for_uid)
async def process_uid(message: types.Message, state: FSMContext):
    if not message.text or not message.text.isdigit():
        await message.answer("❌ **Xato!** Iltimos, faqat raqamlardan iborat bo'lgan UIDni kiriting.\nMasalan: `100234`", parse_mode="Markdown")
        return

    await state.update_data(user_uid=message.text)
    await state.set_state(PaymentSteps.waiting_for_photo)
    await message.answer(
        "📸 **2-bosqich: To'lov chekini yuboring**\n\n"
        "To'lov amalga oshirilganligi haqidagi skrinshotni yoki rasm formatidagi chekni yuboring.\n"
        "_(Iltimos, faqat rasm yuboring)_",
        parse_mode="Markdown"
    )

# Rasm o'rniga matn yuborsa xatolik berish
@dp.message(PaymentSteps.waiting_for_photo, ~F.photo)
async def photo_validation(message: types.Message):
    await message.answer("❌ **Xato!** Iltimos, to'lov chekini **rasm (photo)** holatida yuboring.", parse_mode="Markdown")

@dp.message(PaymentSteps.waiting_for_photo, F.photo)
async def process_photo(message: types.Message, state: FSMContext):
    data = await state.get_data()
    uid = data.get('user_uid')
    
    await bot.send_photo(
        ADMIN_ID,
        message.photo[-1].file_id,
        caption=(
            f"🔔 **YANGI TO'LOV SO'ROVI!**\n"
            f"━━━━━━━━━━━━━━━\n"
            f"👤 **User:** @{message.from_user.username}\n"
            f"🆔 **UID:** `{uid}`\n"
            f"📂 **TG ID:** `{message.from_user.id}`\n"
            f"━━━━━━━━━━━━━━━\n"
            f"⚡️ *Iltimos, to'lovni tekshirib balansni to'ldiring!*"
        ),
        parse_mode="Markdown"
    )
    
    await state.clear()
    await message.answer(
        "✅ **Muvaffaqiyatli!**\n\n"
        "Sizning to'lov so'rovingiz adminga yetkazildi. ⏱ 5-15 daqiqa ichida tekshirilib, balansingiz to'ldiriladi.\n\n"
        "**XERON SHOP**ni tanlaganingiz uchun rahmat! 😊",
        reply_markup=get_main_menu(),
        parse_mode="Markdown"
    )

# --- TAKLIF VA SHIKOYATLAR (CHIROYLIK MATN BILAN) ---
@dp.message(F.text.in_(["💡 Takliflar", "⚠️ Shikoyat", "👨‍💻 Admin bilan bog'lanish"]))
async def support_start(message: types.Message, state: FSMContext):
    await state.set_state(SupportSteps.waiting_for_text)
    await state.update_data(support_type=message.text)
    
    prompts = {
        "💡 Takliflar": "✍️ **Saytimizni yaxshilash bo'yicha taklifingizni yozing:**",
        "⚠️ Shikoyat": "🛠 **Qanday muammoga duch keldingiz? Batafsil tushuntirib bering:**",
        "👨‍💻 Admin bilan bog'lanish": "👨‍💻 **Admin uchun xabaringizni qoldiring:**"
    }
    
    await message.answer(prompts.get(message.text, "Xabaringizni yozing:"), reply_markup=ReplyKeyboardRemove(), parse_mode="Markdown")

@dp.message(SupportSteps.waiting_for_text)
async def support_finish(message: types.Message, state: FSMContext):
    data = await state.get_data()
    s_type = data.get('support_type')
    
    # Adminga yuborish qismi (o'zgarmaydi)
    await bot.send_message(
        ADMIN_ID,
        f"📩 **YANGI MUROJAAT ({s_type})**\n"
        f"━━━━━━━━━━━━━━━\n"
        f"👤 **User:** @{message.from_user.username if message.from_user.username else 'Noma`lum'}\n"
        f"📝 **Matn:** {message.text}\n"
        f"━━━━━━━━━━━━━━━",
        parse_mode="Markdown"
    )
    
    await state.clear()
    
    # Har bir tur uchun alohida javob matni
    if s_type == "💡 Takliflar":
        response_text = (
            "✅ **Taklifingiz qabul qilindi!**\n\n"
            "XERON SHOP jamoasi sizning g'oyangizni albatta ko'rib chiqadi. "
            "Biz foydalanuvchilarimizning fikrlarini qadrlaymiz. "
            "Agar taklifingiz loyihamizga mos kelsa, uni tez orada joriy etamiz! ✨"
        )
    elif s_type == "⚠️ Shikoyat":
        response_text = (
            "✅ **Shikoyatingiz yuborildi.**\n\n"
            "Yuzaga kelgan noqulaylik uchun uzr so'raymiz. 🛠\n"
            "Mutaxassislarimiz muammoni imkon qadar tezroq o'rganib chiqishadi "
            "va uni bartaraf etish choralarini ko'rishadi."
        )
    else:  # Admin bilan bog'lanish uchun
        response_text = (
            "✅ **Xabaringiz adminga yetkazildi.**\n\n"
            "Operatorlarimiz bo'shashi bilan sizga javob berishadi. "
            "Iltimos, biroz kutishingizni so'raymiz. 👨‍💻"
        )
    
    await message.answer(response_text, reply_markup=get_main_menu(), parse_mode="Markdown")

# --- BOSHQA XABARLAR ---
@dp.message()
async def echo_all(message: types.Message):
    await message.answer("⚠️ **Noma'lum buyruq.**\nIltimos, quyidagi menyu tugmalaridan foydalaning:", reply_markup=get_main_menu(), parse_mode="Markdown")

async def main():
    print("Bot ishga tushdi...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())