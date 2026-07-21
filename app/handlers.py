from aiogram import F, Router
from aiogram.filters import CommandStart, Command
from aiogram.types import CallbackQuery, Message

import app.keyboards as kb
import httpx
router = Router()

API_URL = "http://localhost:8000"

### Functions

@router.message(CommandStart())
async def cmd_start(message: Message): 
    await message.reply(
        f"Hello, {message.from_user.first_name}.\n\n"
        f"Search products on eBay.\n"
        f"Press <b>Search</b> to start.",
        parse_mode="HTML",
        reply_markup=kb.main_keyboard)


@router.message(Command('help'))
async def get_help(message: Message):
    await message.answer(
        "<b>How to use:</b>\n\n"
        "1. Press Search\n"
        "2. Type product name\n"
        "3. Get 5 results from eBay",
        parse_mode="HTML"
        )

@router.message(F.text =='Search')
async def search_comand(message:Message):
    await message.answer("Type what you are looking for:")

### language menu

@router.message(F.text =='Language')
async def language_menu(message:Message):
    await message.answer('Choose language:', reply_markup=kb.language_keyboard)

### History menu
@router.message(F.text == "History")
async def history_menu(message:Message):

    # Create link with FastAPI and send GET request on /history/ endpoint to get search history from user by id 
    async with httpx.AsyncClient() as client:
          response = await client.get(f"{API_URL}/search/history/{message.from_user.id}")
    # close link, info was received in JSON format

    #Read answer from FastAPI in JSON format
    data = response.json()

    history = data.get("history", []) # if history is empty, return empty list

    # if histrory is empty, send message to user
    if not history:
        await message.answer("No search history found.")
        return
    
    # Create message with search history and send it to user
    history_text = "<b>Your search history:</b>\n\n"
    for i, item in enumerate(history, 1):
        history_text += f"{i}. {item['query']}\n" # enumerate history and add it to message with number

    await message.answer(history_text, parse_mode="HTML") # send message to user with search history



### return to main menu or search again

@router.message(F.text =='⬅️ Menu')
async def back_to_menu(message:Message):
    await message.answer('Choose category:', reply_markup=kb.main_keyboard)


@router.message(F.text == "🔄 Search again")
async def search_again(message: Message):
    await message.answer("Type what you are looking for:")

#### Search query handler
    
@router.message(F.text & ~F.text.startswith("/")) # search everything except massages started from /
async def search_query(message:Message):
    await message.answer("Searching for: " + message.text) # send message to user that search is in progress

    try: 
        async with httpx.AsyncClient() as client:
              response = await client.post( # start connection with FastAPI and send request
                   f"{API_URL}/search/",
                   json={
                        "query": message.text,
                        "user_id": message.from_user.id,
                        "username": message.from_user.username,
                        "first_name": message.from_user.first_name
                   }
              )

        data = response.json() # read FastAPI answer in JSON

    except Exception as e: # if something went wrong, catch any error, wright user message below. Bot is not crushed
         await message.answer("something went wrong. Try again later.")
         return
    
    items = data.get("items", []) # If Ebay did't found andything, say user and exit
    if not items:
         await message.answer("Nothing found. Try another query.")
         return
        
    for item in items: # Send each item using separate message with button
         text = f"<b>{item['title']}</b>\n{item['price']}\n{item['condition']}"
         await message.answer(text, parse_mode="HTML", reply_markup=kb.item_kb(item["url"]))

    await message.answer("What do you want ot do next?", reply_markup=kb.after_search) # Send navigation button in the end

#search heandlers

@router.callback_query(F.data == "return_to_menu") # take handler from ⬅️ Menu
async def go_home(callback: CallbackQuery):
    await callback.message.answer("Main menu:", reply_markup=kb.main_keyboard)#send message with mainkeyboard
    await callback.answer()# pushing button is nessesery, otherwhise it will load endlessly

@router.callback_query(F.data == "search_again")
async def search_again(callback: CallbackQuery):
    await callback.message.answer("Type what you are looking for:")
    await callback.answer()


