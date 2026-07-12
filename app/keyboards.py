from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

main_keyboard = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Search')],
    [KeyboardButton(text='History'), KeyboardButton(text='Language')]], # main menu

    resize_keyboard=True,
    input_field_placeholder='chose option in menu')


catalog_messages = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="result", callback_data="result")],
    [InlineKeyboardButton(text="result2", callback_data="result2")],
]) # catalog inline messages

language_keyboard = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='English'), KeyboardButton(text='Russian')], 
    [KeyboardButton(text='Uzbek')], 
    [KeyboardButton(text='⬅️ Menu')]],
    resize_keyboard=True, input_field_placeholder='chose language') # language menu
    



get_number = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Send number',request_contact=True)]],
                                 resize_keyboard=True) # number reply keyboard