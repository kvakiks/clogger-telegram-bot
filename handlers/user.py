import os
from aiogram import Router
from aiogram.filters import CommandStart, StateFilter
from aiogram.types import Message, CallbackQuery
from aiogram import F

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

import keyboards.currs as kb_cur
import keyboards.categorrs as kb_cat

from database.models import User
from database.requests import (
    add_expense,
    get_or_create_user,
    get_total_spent_for_days,
    get_users_count,
    get_users_list,
)

user = Router()                             # Рутер

ADMIN_IDS = {
    int(admin_id.strip())
    for admin_id in os.getenv("ADMIN_IDS", "").split(",")
    if admin_id.strip().isdigit()
}

class Test(StatesGroup):                    # Состояния
    choose_currency = State()
    spend = State()


@user.message(CommandStart())                                   # Старт
async def start(message: Message, state: FSMContext, session: AsyncSession):
    user_db = await session.scalar(select(User).where(User.tg_id == message.from_user.id))
    if user_db:
        await state.set_state(Test.spend)
        await message.answer(
            f'С возвращением! Текущая валюта: {user_db.currency}.\n'
            'Продолжай вносить расходы в формате "<категория> <сумма>".',
            reply_markup=kb_cat.main,
        )
        return

    await state.set_state(Test.choose_currency)
    await message.answer(
        'Привет! Я CashLogger — твоя цифровая тетрадь для финансов.\n'
        'Для начала выбери валюту, в которой хочешь вести расчет:',
        reply_markup=kb_cur.main,
    )


currs = ['RUB', 'ILS', 'EUR', 'USD', 'KZT', 'GEL']

@user.callback_query(F.data.in_(currs))                           # Выбор валюты
async def choice(callback: CallbackQuery, state: FSMContext, session: AsyncSession):  
    selected_currency = callback.data
    tg_user_id = callback.from_user.id

    await get_or_create_user(session, tg_user_id, selected_currency)

    # FSM update
    await state.set_state(Test.spend)

    await callback.answer()
    await callback.message.answer(f'Отлично! Твоя валюта: {selected_currency}.\n\nТеперь можешь записывать расходы в формате:\n\n"<категория> <сумма>"\nПример: "Спорт 1500"\n\nСписок категорий доступен по кнопке ниже:', reply_markup=kb_cat.main)


@user.message(F.text == '/admin')
async def admin_panel(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("У тебя нет прав администратора.")
        return

    await message.answer("Админ-панель:", reply_markup=kb_cat.admin)


@user.callback_query(F.data == 'admin_users_count')
async def admin_users_count(callback: CallbackQuery, session: AsyncSession):
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("Нет доступа", show_alert=True)
        return

    users_count = await get_users_count(session)
    await callback.message.answer(f"Количество пользователей: {users_count}")
    await callback.answer()


@user.callback_query(F.data == 'admin_users_list')
async def admin_users_list(callback: CallbackQuery, session: AsyncSession):
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("Нет доступа", show_alert=True)
        return

    users = await get_users_list(session, limit=100)
    if not users:
        await callback.message.answer("Список пользователей пуст.")
        await callback.answer()
        return

    lines = [f"{idx}. {u.tg_id} ({u.currency})" for idx, u in enumerate(users, start=1)]
    await callback.message.answer("Пользователи:\n" + "\n".join(lines))
    await callback.answer()


@user.callback_query(Test.spend, F.data == 'categories')          # Показ списка категорий
async def show_categories(callback: CallbackQuery):
    await callback.message.edit_text(kb_cat.CATEGORIES, parse_mode='HTML', reply_markup=None)
    await callback.answer()


@user.callback_query(Test.spend, F.data == 'reports')
async def show_reports(callback: CallbackQuery):
    await callback.message.answer('Выбери период для отчета:', reply_markup=kb_cat.reports)
    await callback.answer()


REPORT_PERIODS = {
    "report_1d": ("за день", 1),
    "report_7d": ("за неделю", 7),
    "report_14d": ("за 2 недели", 14),
    "report_30d": ("за месяц", 30),
    "report_90d": ("за квартал", 90),
}


@user.callback_query(Test.spend, F.data.in_(list(REPORT_PERIODS)))
async def report_by_period(callback: CallbackQuery, session: AsyncSession):
    tg_user_id = callback.from_user.id
    label, days = REPORT_PERIODS[callback.data]
    total = await get_total_spent_for_days(session, tg_user_id, days)

    user_db = await session.scalar(select(User).where(User.tg_id == tg_user_id))
    if not user_db:
        await callback.message.answer('Вашего профиля не существует. Попробуйте нажать /start')
        await callback.answer()
        return

    await callback.message.answer(f'Твои расходы {label}: {total} {user_db.currency}')
    await callback.answer()


@user.message(Test.spend)
async def spend(message: Message, state: FSMContext, session: AsyncSession):
    user_spent = message.text.strip().split()

    if len(user_spent) != 2:
        await message.answer('Неверный формат.')
        return

    cat_input = user_spent[0].lower()

    if not cat_input in kb_cat.VALID_CATEGORIES:
        await message.answer('Извини, не понял. Убедись, что указана верная категория.')      # Кнопка списка категорий
        return

    if not user_spent[1].isdigit():
        await message.answer('Сумма должна быть целым числом (положительное, без копеек).')
        return

    sum_input = int(user_spent[1])

    saved = await add_expense(session, message.from_user.id, cat_input, sum_input)
    if not saved:
        await message.answer('Вашего профиля не существует. Попробуйте нажать /start')
        return

    await message.answer('Записал.', reply_markup=kb_cat.main)


@user.message(StateFilter(None))
async def restore_state_if_lost(message: Message, state: FSMContext, session: AsyncSession):
    user_db = await session.scalar(select(User).where(User.tg_id == message.from_user.id))
    if not user_db:
        await state.set_state(Test.choose_currency)
        await message.answer('Сначала выбери валюту!', reply_markup=kb_cur.main)
        return

    await state.set_state(Test.spend)
    await message.answer(
        f'Введи расход или выбери команду из меню',
        reply_markup=kb_cat.main,
    )


@user.message(Test.choose_currency)
async def check_chosed_curr(message: Message):
    await message.answer('Сначала выбери валюту!', reply_markup=kb_cur.main)

