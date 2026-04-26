from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

main = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text='RUB', callback_data='RUB'),
        InlineKeyboardButton(text='ILS', callback_data='ILS')
    ],
    [
        InlineKeyboardButton(text='EUR', callback_data='EUR'),
        InlineKeyboardButton(text='USD', callback_data='USD')
    ],
    [
        InlineKeyboardButton(text='KZT', callback_data='KZT'),
        InlineKeyboardButton(text='GEL', callback_data='GEL')]
    ])