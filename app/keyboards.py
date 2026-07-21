from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

main_keyboard = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Search')],
    [KeyboardButton(text='History'), KeyboardButton(text='Language')]], # main menu

    resize_keyboard=True,
    input_field_placeholder='chose option in menu')

# Button under each item
def item_kb(item_url: str):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Buy on Ebay', url=item_url)],
    ])

# button after search result
after_search = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='⬅️ Menu', callback_data='return_to_menu')],
    [KeyboardButton(text='🔄 Search again', callback_data='search_again')]],
    resize_keyboard=True, input_field_placeholder='menu or search again')

language_keyboard = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='English'), KeyboardButton(text='Russian')], 
    [KeyboardButton(text='Uzbek')], 
    [KeyboardButton(text='⬅️ Menu')]],
    resize_keyboard=True, input_field_placeholder='chose language') # language menu
    



get_number = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Send number',request_contact=True)]],
                                 resize_keyboard=True) # number reply keyboard