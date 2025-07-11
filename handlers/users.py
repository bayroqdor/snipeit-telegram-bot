from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from snipe_api import get_users, get_user_by_id, get_user_assets, create_user
from utils.formatter import format_user_list, format_user_details
from keyboards.menus import get_users_menu_keyboard, get_back_button
from keyboards.paginator import get_paginator_keyboard
from telegram.constants import ParseMode

LIMIT = 20
SEARCH, ADD_NAME, ADD_USERNAME, ADD_PASSWORD = range(4)

async def users_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    message_text = "👥 Foydalanuvchilar bo'limi:"
    reply_markup = get_users_menu_keyboard()
    if query:
        await query.answer()
        await query.edit_message_text(text=message_text, reply_markup=reply_markup)
    else:
        await update.message.reply_text(text=message_text, reply_markup=reply_markup)

async def user_list_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    parts = query.data.split('_')
    offset = int(parts[-1])
    search_term = context.user_data.get('user_search_term')

    users_data = await get_users(limit=LIMIT, offset=offset, search=search_term)

    if users_data and 'rows' in users_data:
        message_text = format_user_list(users_data)
        total = users_data.get('total', 0)
        prefix = query.data.rsplit('_', 1)[0]

        reply_markup = get_paginator_keyboard(offset, total, LIMIT, prefix)
        await query.edit_message_text(text=message_text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
    else:
        await query.edit_message_text("Foydalanuvchilar topilmadi yoki yuklashda xatolik.")

async def view_user_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = int(context.args[0])
    except (IndexError, ValueError):
        await update.message.reply_text("Noto'g'ri format. Misol: /view_user 123")
        return

    user_data = await get_user_by_id(user_id)
    user_assets = await get_user_assets(user_id)
    message_text = format_user_details(user_data, user_assets)
    await update.message.reply_html(message_text)

async def search_user_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("🔍 Qidiruv uchun foydalanuvchi ismi, familiyasi yoki username'ini kiriting:",
                                   reply_markup=get_back_button('users_menu'))
    return SEARCH

async def search_user_receive(update: Update, context: ContextTypes.DEFAULT_TYPE):
    search_term = update.message.text
    context.user_data['user_search_term'] = search_term

    users_data = await get_users(search=search_term, limit=LIMIT, offset=0)

    if users_data and users_data.get('total', 0) > 0:
        message_text = f"<b>'{search_term}' bo'yicha qidiruv natijalari:</b>\n\n" + format_user_list(users_data)
        reply_markup = get_paginator_keyboard(0, users_data['total'], LIMIT, "users_list_all")
        await update.message.reply_html(message_text, reply_markup=reply_markup)
    else:
        await update.message.reply_text(f"'{search_term}' bo'yicha hech narsa topilmadi.", reply_markup=get_users_menu_keyboard())

    return ConversationHandler.END

async def add_user_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data['new_user'] = {}
    await query.edit_message_text("Yangi foydalanuvchining to'liq ismini (Ism Familiya) kiriting:",
                                   reply_markup=get_back_button('users_menu'))
    return ADD_NAME

async def add_user_get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name_parts = update.message.text.split(' ', 1)
    context.user_data['new_user']['first_name'] = name_parts[0]
    context.user_data['new_user']['last_name'] = name_parts[1] if len(name_parts) > 1 else ''
    await update.message.reply_text("U uchun username kiriting:")
    return ADD_USERNAME

async def add_user_get_username(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['new_user']['username'] = update.message.text
    await update.message.reply_text("Endi u uchun parol kiriting (kamida 8 ta belgi):")
    return ADD_PASSWORD

async def add_user_get_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    password = update.message.text
    payload = context.user_data['new_user']
    payload.update({
        "password": password,
        "password_confirmation": password,
        "activated": True,
    })

    result = await create_user(payload)

    if result and result.get('status') == 'success':
        message = f"✅ Foydalanuvchi '{payload['first_name']}' muvaffaqiyatli yaratildi!"
        await update.message.reply_text(message, reply_markup=get_users_menu_keyboard())
    else:
        await update.message.reply_text(f"❌ Xatolik: {result.get('messages', 'Noma\'lum xato')}", 
                                        reply_markup=get_users_menu_keyboard())

    context.user_data.clear()
    return ConversationHandler.END
