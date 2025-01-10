
import asyncio
import re
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiohttp import web
from dotenv import load_dotenv
import os

# Import your functions
from functions import getOyat
from functions import getSurah
from db_saver import save_user
from agent_007 import send_to_admin
from surah_list import surah_name_to_number_en, surah_name_to_number_uz
# Load environment variables
load_dotenv()

# Get the token
API_TOKEN = os.getenv("bot_token")
PORT = os.getenv("PORT", "8080")

if not API_TOKEN:
    raise ValueError("The bot token is not set in the .env file.")

# Helper function to split large text into chunks
def split_into_chunks(input_string, max_length):
    parts = []
    while len(input_string) > max_length:
        split_index = input_string[:max_length].rfind(" ")
        if split_index == -1:
            split_index = max_length
        parts.append(input_string[:split_index].strip())
        input_string = input_string[split_index:].strip()
    if input_string:
        parts.append(input_string)
    return parts

async def main():
    # Initialize the bot and dispatcher
    bot = Bot(token=API_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    # User-specific data
    user_language = {}
    user_data = {}

    api_keys = {
        'ar_read': 'ara-kingfahadquranc',
        'uz': 'uzb-muhammadsodikmu',
        'en': 'eng-abdelhaleem',
        'ar': 'ara-quran-la1'
    }

    # Command: /start
    @dp.message(Command(commands=["start"]))
    async def send_welcome(message: Message):
        await message.reply("Hello! This bot is all about Qur'an.\nType any chapter and verse (e.g. 78:8 or 17 or al-baqara or baqara 5).")

    # Command: /help
    @dp.message(Command(commands=["help"]))
    async def send_help(message: Message):
        await message.reply("Contact: @Bestoftheplayers")

    # Command: /languages
    @dp.message(Command(commands=["languages"]))
    async def choose_language(message: Message):
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="English 🇬🇧", callback_data="lang_en")],
                [InlineKeyboardButton(text="Arabic 🇸🇦", callback_data="lang_ar")],
                [InlineKeyboardButton(text="Uzbek 🇺🇿", callback_data="lang_uz")]
            ]
        )
        await message.answer("Choose a language:", reply_markup=keyboard)

    # Callback handler: Language selection
    @dp.callback_query(F.data.startswith("lang"))
    async def handle_language_selection(callback_query: CallbackQuery):
        user_id = callback_query.from_user.id
        if callback_query.data == "lang_en":
            user_language[user_id] = "en"
            await callback_query.message.edit_text("You selected English 🇬🇧")
        elif callback_query.data == "lang_ar":
            user_language[user_id] = "ar"
            await callback_query.message.edit_text("You selected Arabic 🇸🇦")
        elif callback_query.data == "lang_uz":
            user_language[user_id] = "uz"
            await callback_query.message.edit_text("You selected Uzbek 🇺🇿")
        await callback_query.answer()

    # Function: Navigation keyboard
    def navigation_keyboard(index: int, total: int) -> InlineKeyboardMarkup:
        keyboard = []
        if index > 0:
            keyboard.append(InlineKeyboardButton(text="<< Previous", callback_data=f"prev:{index}"))
        if index < total - 1:
            keyboard.append(InlineKeyboardButton(text="Next >>", callback_data=f"next:{index}"))
        return InlineKeyboardMarkup(inline_keyboard=[keyboard])

    # Message handler: Process user inputs
    @dp.message()
    async def handle_message(message: Message):
        user = message.from_user
        user_id = user.id
        name = user.first_name
        username = user.username or "N/A"
        message_text = message.text

        try:
            save_user(user_id, username, name)
            send_to_admin(username, user_id, message_text)
        except Exception as e:
            print(f"Error saving user or sending to admin: {e}")

        if user_id not in user_language:
            await message.reply("Please select a language first using /languages.")
            return

        language = user_language[user_id]
        
        if re.fullmatch(r"\d+", message_text):
            surah_number = int(message_text)
            tafsir = api_keys.get(language)
            verses, error = getSurah(tafsir, surah_number)
            if error:
                await message.reply(error)
                return

            user_data[user_id] = {"verses": verses, "index": 0}
            await message.reply(verses[0], reply_markup=navigation_keyboard(0, len(verses)), parse_mode = "HTML")
       
        elif re.fullmatch(r"\d+:\d+", message_text):
            surah_number, ayah_number = map(int, message_text.split(":"))
            response = getOyat(api_keys.get(language), surah_number, ayah_number)
            await message.reply(response or "Could not fetch Ayah.", parse_mode='HTML')
       
        elif re.fullmatch(r"[a-zA-Z\-]+(\s+\d+(-oyat)?)?", message_text):  # Updated regex
            message_text = message_text.lower()  # Ensure the surah name is in lowercase
            parts = message_text.split()
            surah_name = parts[0]

            # Check if surah name is valid in English or Uzbek
            surah_number = surah_name_to_number_en.get(surah_name) or surah_name_to_number_uz.get(surah_name)
            if not surah_number:
                await message.reply("Invalid surah name. Please provide a valid surah name.")
                return

            if len(parts) == 2:
                try:
                    # Check if Ayah is provided
                    ayah_number = int(parts[1].replace("-oyat", "").strip())  # Handle numbers with or without '-oyat'
                    response = getOyat(api_keys.get(language), surah_number, ayah_number)
                    await message.reply(response or "Could not fetch Ayah.", parse_mode="HTML")
                except ValueError:
                    await message.reply("Invalid Ayah number format. Use '<surah> <number>' or '<surah> <number>-oyat'.")
                except Exception as e:
                    await message.reply(f"An error occurred: {e}")
            elif len(parts) == 1:
                try:
                    # Fetch Surah verses
                    tafsir = api_keys.get(language)
                    verses, error = getSurah(tafsir, surah_number)

                    if error:
                        await message.reply(error)
                        return

                    # Store user data and send the first verse
                    user_data[user_id] = {"verses": verses, "index": 0}
                    await message.reply(verses[0], reply_markup=navigation_keyboard(0, len(verses)), parse_mode="HTML")
                except KeyError:
                    await message.reply("Language not supported or invalid API key.")
                except Exception as e:
                    await message.reply(f"An error occurred while fetching the surah: {e}")
            else:
                await message.reply("Invalid input format. Use '<surah>' or '<surah> <number>' or '<surah> <number>-oyat'.")

        else:
            await message.reply('Please check the input again')
    # Callback handler: Navigation
    @dp.callback_query(F.data.startswith(("next", "prev")))
    async def navigate(callback: CallbackQuery):
        user_id = callback.from_user.id
        if user_id not in user_data:
            await callback.answer("Please fetch a Surah first.")
            return

        action, current_index = callback.data.split(":")
        current_index = int(current_index)
        verses = user_data[user_id]["verses"]
        total_verses = len(verses)

        if action == "next":
            current_index = (current_index + 1) % total_verses
        elif action == "prev":
            current_index = (current_index - 1) % total_verses

        user_data[user_id]["index"] = current_index
        await callback.message.edit_text(verses[current_index], reply_markup=navigation_keyboard(current_index, total_verses), parse_mode="HTML")
        await callback.answer()

    # Dummy web server for deployment
    app = web.Application()
    app.router.add_get("/", lambda _: web.Response(text="Bot is running!"))

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", int(PORT))
    await site.start()

    print(f"Server running on port {PORT}")
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())

