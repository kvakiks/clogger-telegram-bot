from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

main = InlineKeyboardMarkup(inline_keyboard=[
        InlineKeyboardButton(text='Список категорий', callback_data='categories')
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

    footer = '\n\nВведи "<категория> <сумма>" в чат, чтобы внести расход\nПример: "Еда 470"'
    
    return header + '\n'.join(lines) + footer

CATEGORIES = get_simple_formatted_list(categories)          # Форматированные категории

VALID_CATEGORIES = [
    'жилье', 'продукты', 'транспорт', 'здоровье', 'связь', 'еда', 
    'одежда', 'красота', 'обучение', 'досуг', 'подписки', 'спорт', 
    'подарки', 'дети', 'питомцы', 'техника', 'долги', 'инвестиции', 
    'налоги', 'прочее'
]