from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

main = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text='Список категорий', callback_data='categories'),
        InlineKeyboardButton(text='Отчет по расходам', callback_data='reports'),
    ]
])

reports = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text='День', callback_data='report_1d'),
        InlineKeyboardButton(text='Неделя', callback_data='report_7d'),
    ],
    [
        InlineKeyboardButton(text='2 недели', callback_data='report_14d'),
        InlineKeyboardButton(text='Месяц', callback_data='report_30d'),
    ],
    [
        InlineKeyboardButton(text='Квартал', callback_data='report_90d'),
    ],
])

admin = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text='Количество пользователей', callback_data='admin_users_count'),
        InlineKeyboardButton(text='Список пользователей', callback_data='admin_users_list'),
    ]
])

help = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Написать разработчикам', callback_data='help_contact_devs')],
])

categories = [
    '🏠 Жилье', '🛒 Продукты', '🚗 Транспорт', '💊 Здоровье',
    '📶 Связь', '🍱 Еда', '👕 Одежда', '💅 Красота',
    '📚 Обучение', '🎭 Досуг', '☁️ Подписки', '⚽ Спорт',
    '🎁 Подарки', '👶 Дети', '🐾 Питомцы', '🎧 Техника',
    '💸 Долги', '📈 Инвестиции', '⚖️ Налоги', '📦 Прочее'
]

def get_simple_formatted_list(cats):
    header = '<b>         Список категорий:</b>\n<i>    (нажми для копирования)</i>\n\n'
    
    pairs = [item.split(' ', 1) for item in cats]
    max_label_len = max(len(p[1]) for p in pairs)
    
    lines = []
    for i in range(0, len(pairs), 2):
        l_icon, l_name = pairs[i]
        left_col = f"{l_icon} <code>{l_name.ljust(max_label_len)}</code>"
        
        row = left_col
        if i + 1 < len(pairs):
            r_icon, r_name = pairs[i+1]
            right_col = f"{r_icon} <code>{r_name}</code>"
            row = f"{left_col}   {right_col}"
            
        lines.append(row)

    footer = '\n\nВведи "&lt;категория&gt; &lt;сумма&gt;" в чат\n\nПример: "Еда 470"'
    return header + '\n\n'.join(lines) + footer

CATEGORIES = get_simple_formatted_list(categories)


VALID_CATEGORIES = [
    'жилье', 'продукты', 'транспорт', 'здоровье', 'связь', 'еда', 
    'одежда', 'красота', 'обучение', 'досуг', 'подписки', 'спорт', 
    'подарки', 'дети', 'питомцы', 'техника', 'долги', 'инвестиции', 
    'налоги', 'прочее'
]