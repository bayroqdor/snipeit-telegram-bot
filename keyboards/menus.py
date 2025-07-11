from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup

def get_main_menu_keyboard():
    keyboard = [['🗄 Aktivlar (Assets)'], ['👥 Foydalanuvchilar (Users)']]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)

def get_assets_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("Barcha aktivlar", callback_data='assets_list_all_0')],
        [InlineKeyboardButton("Topshirishga tayyor", callback_data='assets_list_rtd_0'),
         InlineKeyboardButton("Topshirilgan", callback_data='assets_list_deployed_0')],
        [InlineKeyboardButton("🔍 Qidirish", callback_data='assets_search_start')],
        [InlineKeyboardButton("➕ Yangi qo'shish", callback_data='assets_add_start')],
    ]
    return InlineKeyboardMarkup(keyboard)

def get_users_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("Barcha foydalanuvchilar", callback_data='users_list_all_0')],
        [InlineKeyboardButton("🔍 Qidirish", callback_data='users_search_start')],
        [InlineKeyboardButton("➕ Yangi qo'shish", callback_data='users_add_start')],
    ]
    return InlineKeyboardMarkup(keyboard)

def get_asset_actions_keyboard(asset_id):
    keyboard = [[
        InlineKeyboardButton("👤 Biriktirish", callback_data=f"asset_assign_start_{asset_id}"),
    ]]
    return InlineKeyboardMarkup(keyboard)

def get_back_button(menu_callback):
    return InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Orqaga", callback_data=menu_callback)]])