from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

main = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Список категорий', callback_data='categories')],
    [InlineKeyboardButton(text='Отчет по расходам', callback_data='reports')]
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
    [InlineKeyboardButton(text='Количество пользователей', callback_data='admin_users_count')],
    [InlineKeyboardButton(text='Список пользователей', callback_data='admin_users_list')],
])

categories = [
    '🏠 Жилье', '🛒 Продукты', '🚗 Транспорт', '💊 Здоровье',
    '📱 Связь', '🍕 Еда', '👕 Одежда', '💅 Красота',
    '📚 Обучение', '🎭 Досуг', '💳 Подписки', '⚽ Спорт',
    '🎁 Подарки', '👶 Дети', '🐾 Питомцы', '💻 Техника',
    '💸 Долги', '📈 Инвестиции', '⚖️ Налоги', '🌀 Прочее'
]

def get_simple_formatted_list(cats):
    header = '<b>💡 Список категорий:</b>\n<i>(нажми для копирования)</i>\n\n'
    
    lines = []
    for i in range(0, len(cats), 2):
        pair = []
        for item in cats[i:i+2]:
            icon, name = item.split(' ', 1)
            pair.append(f'{icon} <code>{name}</code>')
        
        lines.append('    '.join(pair))

    footer = '\n\nВведи "&lt;категория&gt; &lt;сумма&gt;" в чат, чтобы внести расход\nПример: "Еда 470"'
    
    return header + '\n'.join(lines) + footer

CATEGORIES = get_simple_formatted_list(categories)          # Форматированные категории

VALID_CATEGORIES = [
    'жилье', 'продукты', 'транспорт', 'здоровье', 'связь', 'еда', 
    'одежда', 'красота', 'обучение', 'досуг', 'подписки', 'спорт', 
    'подарки', 'дети', 'питомцы', 'техника', 'долги', 'инвестиции', 
    'налоги', 'прочее'
]