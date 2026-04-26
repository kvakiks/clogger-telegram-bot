from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram import F

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

import keyboards.currs as kb_cur

from database.models import User, Consumption

import keyboards.categorrs as kb_cat

user = Router()                             # Рутер

class Test(StatesGroup):                    # Состояния
    choose_currency = State()
    spend = State()


@user.message(CommandStart())                                   # Старт
async def start(message: Message, state: FSMContext):
    await state.set_state(Test.choose_currency)
    await message.answer(f'Привет! Я CashLogger — твоя цифровая тетрадь для финансов.\nДля начала выбери валюту, в которой хочешь вести расчет:', reply_markup=kb_cur.main)


currs = ['RUB', 'ILS', 'EUR', 'USD', 'KZT', 'GEL']

@user.callback_query(Test.choose_currency, F.data.in_(currs))                           # Выбор валюты
async def choice(callback: CallbackQuery, state: FSMContext, session: AsyncSession):  
    selected_currency = callback.data
    tg_user_id = callback.from_user.id

    user_db = await session.scalar(select(User).where(User.tg_id == tg_user_id))

    if not user_db:
        session.add(User(tg_id=tg_user_id, currency=selected_currency))
    else:
        user_db.currency = selected_currency
    
    await session.commit()

    # FSM update
    await state.set_state(Test.spend)

    await callback.answer()
    await callback.message.answer(f'Отлично! Твоя валюта: {selected_currency}.\n\nТеперь можешь записывать расходы в формате:\n\n"<категория> <сумма>"\nПример: "Спорт 1500"\n\nСписок категорий доступен по кнопке ниже:', reply_markup=kb_cat.main)


@user.callback_query(Test.spend, F.data == 'categories')          # Показ списка категорий
async def show_categories(callback: CallbackQuery):
    await callback.message.edit_text(kb_cat.CATEGORIES, parse_mode='HTML', reply_markup=None)
    await callback.answer()


@user.message(Test.spend)
async def spend(message: Message, state: FSMContext, session: AsyncSession):
    user_spent = message.text.strip().split()

    if len(user_spent) != 2:
        await message.answer('Неверный формат.')
        return

    cat_input = user_spent[0].lower()

    if not cat_input in kb_cat.VALID_CATEGORIES:
        await message.answer('Извини, не понял. Проверь правильность указания категории.')      # Кнопка списка категорий
        return

    if not user_spent[1].isdigit():
        await message.answer('Сумма должна быть целым числом (положительное, без копеек).')
        return

    sum_input = int(user_spent[1])

    # Пут в БД
    user_db = await session.scalar(select(User).where(User.tg_id == message.from_user.id))

    if not user_db:                                 # Подумать над логикой отсутсвия юзера
        await message.answer('Вашего профиля не существует. Попробуйте нажать /start')
        return

    expense = Consumption(
        consumer_id=user_db.tg_id,
        category=cat_input,
        spent=sum_input,
    )

    session.add(expense)
    await session.commit()

    await message.answer('Записал.')        # Кнопка отчет за день + все отчеты


@user.message(Test.choose_currency)
async def check(message: Message):          # Проверка, что валюта выбрана
    await message.answer('Сначала выбери валюту!', reply_markup=kb_cur.main)