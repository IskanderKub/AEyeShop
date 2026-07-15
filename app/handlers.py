from aiogram import F, Router
from aiogram.filters import CommandStart, Command
from aiogram.types import CallbackQuery, Message

from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

import app.keyboards as kb

router = Router()

class Register(StatesGroup):
    name = State()
    age = State()
    number = State()




### field of regestration

@router.message(Command('register'))
async def register(message:Message, state: FSMContext):
    await state.set_state(Register.name)
    await message.answer('type your name ')

@router.message(Register.name)
async def register_name(message: Message, state:FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(Register.age)
    await message.answer('type your age')

@router.message(Register.age)
async def register_age(message: Message, state: FSMContext):
    await state.update_data(age=message.text)
    await state.set_state(Register.number)
    await message.answer("type your phone number", reply_markup=kb.get_number)

@router.message(Register.number, F.contact)
async def register_phone_number(message: Message, state: FSMContext):
    await state.update_data(phone_number=message.contact)
    data = await state.get_data()
    await message.answer(f'Your name: {data["name"]}\nYour age: {data["age"]}\nPhone number: {data["phone_number"]}')
    await state.clear()

###callback query

@router.callback_query(F.data =='result')
async def t_shirt(callback: CallbackQuery):
    await callback.answer('You chosed category')
    await callback.message.answer('You chosed category RESULT`')

### Functions

@router.message(Command('start'))
async def catalog(message:Message):
    await message.answer('Chouse category:', reply_markup=kb.main_keyboard)
    
@router.message(CommandStart())
async def cmd_start(message: Message): 
    await message.reply(f'Hello \nYour ID: {message.from_user.id}\nName: {message.from_user.first_name}', reply_markup=kb.main_keyboard)


@router.message(Command('help'))
async def get_help(message: Message):
    await message.answer("This is the comand /help")

@router.message(F.text =='Search')
async def catalog(message:Message):
    await message.answer('Chouse category:', reply_markup=kb.catalog_messages)


### language menu

@router.message(F.text =='Language')
async def catalog(message:Message):
    await message.answer('Chouse category:', reply_markup=kb.language_keyboard)

@router.message(F.text =='⬅️ Menu')
async def back_to_menu(message:Message):
    await message.answer('Chouse category:', reply_markup=kb.main_keyboard)