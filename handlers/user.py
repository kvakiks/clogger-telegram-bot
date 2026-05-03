import os

from dotenv import load_dotenv
load_dotenv()

from aiogram import Router
from aiogram.filters import Command, CommandStart, StateFilter
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
    get_spending_by_category_for_days,
    get_users_count,
    get_users_list,
)

user = Router()                             

ADMIN_IDS = {
    int(admin_id.strip())
    for admin_id in os.getenv("ADMIN_IDS", "").split(",")
    if admin_id.strip().isdigit()
}

dev = os.getenv("DEVELOPERS_CONTACT")

class Test(StatesGroup):               
    choose_currency = State()
    spend = State()


@user.message(CommandStart())                                 
async def start(message: Message, state: FSMContext, session: AsyncSession):
    await state.clear()
    user_db = await session.scalar(select(User).where(User.tg_id == message.from_user.id))
    if user_db:
        await state.set_state(Test.spend)
        await message.answer(
            f'Бот перезапущен. Текущая валюта: {user_db.currency}.\n'
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

@user.message(Command('help'))
async def help_command(message: Message):
    text = '<i>Как пользоваться?</i>\n\nПросто записывай расходы в формате &lt;категория&gt; &lt;сумма&gt;, бот все посчитает и по запросу предоставит сводку.\n\nОтчеты и другие команды находятся в меню слева.\n\n⏬ Обратная связь ⏬'
    await message.answer(text, parse_mode='HTML', reply_markup=kb_cat.help)


@user.message(Command('categories'))
async def categories_command(message: Message):
    await message.answer(kb_cat.CATEGORIES, parse_mode='HTML')


@user.callback_query(F.data == 'help_categories')
async def help_categories_callback(callback: CallbackQuery):
    await callback.message.edit_text(kb_cat.CATEGORIES, parse_mode='HTML', reply_markup=None)
    await callback.answer()


@user.callback_query(F.data == 'help_contact_devs')
async def help_contact_devs_callback(callback: CallbackQuery):
    await callback.message.edit_text(f'Напиши разработчикам: {dev}')
    await callback.answer()


currs = ['RUB', 'ILS', 'EUR', 'USD', 'KZT', 'GEL']

@user.callback_query(F.data.in_(currs))                          
async def choice(callback: CallbackQuery, state: FSMContext, session: AsyncSession):  
    selected_currency = callback.data
    tg_user_id = callback.from_user.id
    user_db = await session.scalar(select(User).where(User.tg_id == tg_user_id))

    if user_db:
        await state.set_state(Test.spend)
        await callback.answer(f"Валюта уже выбрана, для смены пиши {dev}")
        return

    await get_or_create_user(session, tg_user_id, selected_currency)

    await state.set_state(Test.spend)

    await callback.answer()
    await callback.message.answer(f'Отлично! Твоя валюта: {selected_currency}.\n\nТеперь можешь записывать расходы в формате:\n\n"<категория> <сумма>"\nПример: "Спорт 1500"\n\n⏬ Список категорий доступен по кнопке ниже:', reply_markup=kb_cat.main)


@user.message(F.text == '/admin')
async def admin_panel(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("У тебя нет прав администратора.")
        return

    await message.answer("Админ-панель:", reply_markup=kb_cat.admin)


@user.callback_query(F.data == 'admin_users_count')
async def admin_users_count(callback: CallbackQuery, session: AsyncSession):
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("Нет доступа")
        return

    users_count = await get_users_count(session)
    await callback.message.answer(f"Количество пользователей: {users_count}")
    await callback.answer()


@user.callback_query(F.data == 'admin_users_list')
async def admin_users_list(callback: CallbackQuery, session: AsyncSession):
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("Нет доступа")
        return

    users = await get_users_list(session, limit=100)
    if not users:
        await callback.message.answer('Список пользователей пуст.')
        await callback.answer()
        return

    lines = [f"{idx}. {u.tg_id} ({u.currency})" for idx, u in enumerate(users, start=1)]
    await callback.message.answer("Пользователи:\n" + "\n".join(lines))
    await callback.answer()


@user.callback_query(Test.spend, F.data == 'categories')          
async def show_categories(callback: CallbackQuery):
    await callback.message.edit_text(kb_cat.CATEGORIES, parse_mode='HTML', reply_markup=None)
    await callback.answer()


@user.callback_query(Test.spend, F.data == 'reports')
async def show_reports(callback: CallbackQuery):
    await send_reports_menu(callback.message)
    await callback.answer()


@user.message(Test.spend, Command('reports'))
async def show_reports_command(message: Message):
    await send_reports_menu(message)


async def send_reports_menu(message: Message):
    await message.answer('Выбери период для отчета:', reply_markup=kb_cat.reports)


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

    user_db = await session.scalar(select(User).where(User.tg_id == tg_user_id))
    if not user_db:
        await callback.message.answer('Вашего профиля не существует. Попробуйте нажать /start')
        await callback.answer()
        return

    breakdown, total = await get_spending_by_category_for_days(session, tg_user_id, days)
    cur = user_db.currency

    if not breakdown:
        text = f'<b>Расходы {label}</b>\n\nЗа этот период записей нет.\n\n<b>Итого: 0 {cur}</b>'
    else:
        lines = [f'<b>Расходы {label}</b>\n']
        for cat, amount in breakdown:
            lines.append(f'— <i>{cat.capitalize()}</i>:   {amount}')
        lines.extend(['', f'<b>Итого: {total} {cur}</b>'])
        text = '\n'.join(lines)

    await callback.message.edit_text(text, parse_mode='HTML')
    await callback.answer()


@user.message(Test.spend)
async def spend(message: Message, state: FSMContext, session: AsyncSession):
    user_spent = message.text.strip().split()

    if len(user_spent) != 2:
        await message.answer('Неверный формат.')
        return

    cat_input = user_spent[0].lower()

    if not cat_input in kb_cat.VALID_CATEGORIES:
        await message.answer('Извини, не понял. Убедись, что указана верная категория.')      
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

