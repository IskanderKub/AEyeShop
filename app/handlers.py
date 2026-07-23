from aiogram import F, Router
from aiogram.filters import CommandStart, Command
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

import app.keyboards as kb
import httpx
router = Router()

API_URL = "http://localhost:8000"

# store last search query and offset for each user
user_search_state = {}  # {user_id: {"query": "thinkpad", "offset": 5}}

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

@router.message(F.text =='🔎 Search')
async def search_comand(message:Message):
    await message.answer("Type what you are looking for:")

### language menu

#@router.message(F.text =='Language')
#async def language_menu(message:Message):
#    await message.answer('Choose language:', reply_markup=kb.language_keyboard)

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


###Track Price logic 

class TrackPrice(StatesGroup):
    waiting_for_price = State()

@router.callback_query(F.data.startswith("track_")) # hendler activates when user pushes the button
async def track_price(callback: CallbackQuery, state: FSMContext): # take 2 parameters: activated button and FSM - state for keeping dates between messages
    item_id = callback.data.split("_", 1)[1] #Take item_id from callback_data "track_v1|123456" → "v1|123456".


    #save item_id in FSM state to use later
    await state.update_data(item_id=item_id) # Save item_id in FSM when user texted price of item we need to track it by id
    await state.set_state(TrackPrice.waiting_for_price) #  turn bot in state of waiting price

    await callback.message.answer("at what price should I notify you? (enter number)") # Ask price and and close loading button
    await callback.answer()

@router.message(TrackPrice.waiting_for_price)
async def save_track_price(message: Message, state: FSMContext):

    #get item_id form FSM state
    data = await state.get_data()
    item_id = data["item_id"]

    #chack if user entered vaild number
    try:
        target_price = float(message.text)
    except ValueError:
        await message.answer("Please enter a vaild number. Example: 200")
        return

    # send dates in FastAPI with new endpoints /tracker/add and save note in price_tracker
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{API_URL}/tracker/add",
            json = {
                "user_id": message.from_user.id,
                "item_id": item_id,
                "target_price": target_price
            }
        )

    await state.clear() #close FSM state
    await message.answer(f"Done! I'll notify you when price drops below ${target_price}") # send message with price typed by user

###  More results logic
@router.message(F.text == "➕ More results")
async def more_results(message:Message):

    # check does previous search existed for this user
    user_id = message.from_user.id
    if user_id not in user_search_state: # if not send him this message
        await message.answer("No previous search found. Press Search first.")
        return


    # get last query and increase offset by 5 from previouse request
    state = user_search_state[user_id]
    query = state["query"]
    offset = state["offset"] + 5
    user_search_state[user_id]["offset"] = offset

    await message.answer(f"Loading more results for: {query}") # send user what we are searching

    try:
        async with httpx.AsyncClient() as client: # Send Post request with /search/ endpoint on FastAPI
            response = await client.post(
            f"{API_URL}/search/",
            json={
                "query": query,
                "user_id": user_id,
                "username": message.from_user.username,
                "first_name": message.from_user.first_name,
                "offset": offset # main difference from casual search
                }
            )
        data = response.json() # dates will be written in json

    except Exception as e: # if something went wrong send this message to user
        await message.answer("Something went wrong. Try again later.")
        return

    items = data.get("items", []) # if items was not found send this message
    if not items:
        await message.answer("No more resutls found")
        return

    for item in items: # take info from eBay (title, price, condition and image) and send it in message for user
        text = f"<b>{item['title']}</b>\n{item['price']}\n{item['condition']}"
        if item.get("image"):
            await message.answer_photo(
                photo = item["image"],
                caption = text,
                parse_mode = "HTML",
                reply_markup = kb.item_kb(item["url"], item["item_id"]) 
            )
        else: # if item does not have picture just send url
            await message.answer(text, parse_mode="HTML", reply_markup=kb.item_kb(item["url"], item["item_id"]))

    await message.answer("What do you want to do next?", reply_markup=kb.after_search) # after all algoritm send keyboard(Search again, More results, Menu )
    

#### Search query handler
    
@router.message(F.text & ~F.text.startswith("/")) # search everything except massages started from /
async def search_query(message:Message):
    await message.answer("Searching for: " + message.text) # send message to user that search is in progress

    # save query and reset offset for this user
    user_search_state[message.from_user.id] = {
        "query": message.text,
        "offset": 0
    }



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
        if item.get("image"): #if photo exits
             await message.answer_photo(
                 photo=item["image"],
                 caption=text,
                 parse_mode="HTML",
                 reply_markup=kb.item_kb(item["url"], item["item_id"])
             )
        else: # if photo doesn't exit, just send text
         await message.answer(text, parse_mode="HTML", reply_markup=kb.item_kb(item["url"]))

    await message.answer("What do you want ot do next?", reply_markup=kb.after_search) # Send navigation button in the end


###Details logic 

@router.callback_query(F.data.startswith("details_")) #Heandler for Details button
async def show_details(callback: CallbackQuery):
    item_id = callback.data.split("_", 1)[1]

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{API_URL}/search/item/{item_id}")#Send GET requsert from item_id, FastAPI take answer from eBay

    data = response.json() # Put answer in JSON

    text = ( # fields for answer to user
        f"<b>{data.get('title', 'N/A')}</b>\n\n"
        f"💰 {data.get('price', 'N/A')}\n"
        f"📍 {data.get('condition', 'N/A')}\n"
        f"👤 Seller: {data.get('seller', 'N/A')}\n\n"
        f"📋 {data.get('description', 'No description')}"
    )

    # Send details to user and close button loading
    await callback.message.answer(text, parse_mode = "HTML")
    await callback.answer()

