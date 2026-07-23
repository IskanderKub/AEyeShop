from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

main_keyboard = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='🔎 Search')],
    [KeyboardButton(text='🏛 History')]], # main menu

    resize_keyboard=True,
    input_field_placeholder='chose option in menu')

# Button under each item
def item_kb(item_url: str, item_id: str):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
    InlineKeyboardButton(text='🛒 Buy on eBay', url=item_url),
    InlineKeyboardButton(text='📋 Details', callback_data=f"details_{item_id}") 
        ],
        [
    InlineKeyboardButton(text='📊 Track Price', callback_data=f"track_{item_id}")
        ]
    ])

after_search = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='⬅️ Menu')],
    [KeyboardButton(text='🔄 Search again'), KeyboardButton(text='➕ More results')]],
    resize_keyboard=True, input_field_placeholder='menu or search again') # After search result will be option go to mainkb or search again

language_keyboard = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='English'), KeyboardButton(text='Russian')], 
    [KeyboardButton(text='Uzbek')], 
    [KeyboardButton(text='⬅️ Menu')]],
    resize_keyboard=True, input_field_placeholder='chose language') # language menu
    

history_actions_kb = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='🧮 Delete specific')],
    [KeyboardButton(text='🗑 Delete All')],
    [KeyboardButton(text='⬅️ Menu')]],
    resize_keyboard=True,
    input_field_placeholder='Choose action') # keyboard to delete history of requests


get_number = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Send number',request_contact=True)]],
                                 resize_keyboard=True) # number reply keyboard