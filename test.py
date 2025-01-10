import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.filters import CommandStart, Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

API_TOKEN = "7818707015:AAFejca3Qct648RgNCgZYsV29LiWMtk9KE8"  # Replace with your bot token

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Simple data to display
data = ["Text 1: Hello!", "Text 2: How are you?", "Text 3: Welcome!", "Text 4: Goodbye!"]

# User index storage
user_index = {}


# Function to create navigation buttons
def navigation_keyboard(index: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="<< Previous", callback_data=f"prev:{index}")
    builder.button(text="Next >>", callback_data=f"next:{index}")
    return builder.as_markup()


# Start command handler
@dp.message(CommandStart())
async def start(message: types.Message):
    user_id = message.from_user.id
    user_index[user_id] = 0  # Start at the first text
    current_index = 0
    text = data[current_index]
    await message.answer(text, reply_markup=navigation_keyboard(current_index))


# Callback query handler for navigation
@dp.callback_query(F.data.startswith(("next", "prev")))
async def navigate(callback: CallbackQuery):
    user_id = callback.from_user.id
    action, current_index = callback.data.split(":")
    current_index = int(current_index)

    # Adjust the index
    if action == "next":
        current_index = (current_index + 1) % len(data)
    elif action == "prev":
        current_index = (current_index - 1) % len(data)

    user_index[user_id] = current_index
    await callback.message.edit_text(data[current_index], reply_markup=navigation_keyboard(current_index))
    await callback.answer()


# Main function to start polling
async def main():
    print("Bot started...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())


# from aiogram import Bot, Dispatcher, types
# from aiogram.filters import CommandStart
# from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
# from aiogram.utils.keyboard import InlineKeyboardBuilder
# import requests
# import asyncio

# API_TOKEN = "your_bot_api_token"  # Replace with your Telegram Bot API token

# bot = Bot(token=API_TOKEN)
# dp = Dispatcher()

# user_index = {}  # To track user navigation
# user_data = {}   # To store fetched verses for users


# # Function to fetch verse
# def get_verse(tafsir, sura, oyat):
#     try:
#         url_oyat1 = f"https://cdn.jsdelivr.net/gh/fawazahmed0/quran-api@1/editions/{tafsir}/{sura}.json"
#         url_oyat2 = f"https://cdn.jsdelivr.net/gh/fawazahmed0/quran-api@1/editions/{tafsir}/{sura}/{oyat}.json"
#         r1 = requests.get(url_oyat1)
#         res1 = r1.json()

#         total_verses = len(res1['chapter'])
#         if oyat > total_verses:
#             return None, "The verse number you input exceeded the total number of verses in this chapter. Please try again."
        
#         r2 = requests.get(url_oyat2)
#         res2 = r2.json()
#         chapters = f"{res2['chapter']}:{res2['verse']} - "
#         ayah = f"{res2['text']}"
#         return chapters + ayah, None
#     except Exception as e:
#         return None, str(e)


# # Function to create navigation buttons
# def navigation_keyboard(index: int, total: int) -> InlineKeyboardMarkup:
#     builder = InlineKeyboardBuilder()
#     if index > 0:
#         builder.button(text="<< Previous", callback_data=f"prev:{index}")
#     if index < total - 1:
#         builder.button(text="Next >>", callback_data=f"next:{index}")
#     return builder.as_markup()


# # Start command handler
# @dp.message(CommandStart())
# async def start(message: types.Message):
#     user_id = message.from_user.id

#     # Fetch chapter data (example tafsir, sura)
#     tafsir = "en.sahih"  # Example tafsir
#     sura = 1             # Example chapter
#     total_verses = 7     # Example total verses

#     user_data[user_id] = []
#     for i in range(1, total_verses + 1):
#         verse, error = get_verse(tafsir, sura, i)
#         if error:
#             await message.answer(error)
#             return
#         user_data[user_id].append(verse)

#     user_index[user_id] = 0
#     current_index = 0
#     text = user_data[user_id][current_index]
#     await message.answer(text, reply_markup=navigation_keyboard(current_index, total_verses))


# # Callback query handler for navigation
# @dp.callback_query(lambda c: c.data.startswith(("next", "prev")))
# async def navigate(callback: CallbackQuery):
#     user_id = callback.from_user.id
#     total = len(user_data[user_id])
#     action, current_index = callback.data.split(":")
#     current_index = int(current_index)

#     # Adjust the index
#     if action == "next" and current_index < total - 1:
#         current_index += 1
#     elif action == "prev" and current_index > 0:
#         current_index -= 1

#     user_index[user_id] = current_index
#     text = user_data[user_id][current_index]
#     await callback.message.edit_text(text, reply_markup=navigation_keyboard(current_index, total))
#     await callback.answer()


# # Main function to start polling
# async def main():
#     print("Bot started...")
#     await dp.start_polling(bot)


# if __name__ == "__main__":
#     asyncio.run(main())
