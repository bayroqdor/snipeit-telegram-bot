from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from telegram.constants import ParseMode
from snipe_api import get_assets, get_asset_by_id, get_users, assign_asset, create_asset, get_models, get_status_labels
from utils.formatter import format_asset_list, format_asset_details, format_selection_keyboard
from keyboards.menus import get_assets_menu_keyboard, get_asset_actions_keyboard, get_back_button
from keyboards.paginator import get_paginator_keyboard

LIMIT = 20

(SEARCH, ADD_NAME, ADD_TAG, ADD_MODEL, ADD_STATUS, ASSIGN_USER) = range(6)

async def assets_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    message_text = "🗄️ Aktivlar bo'limi:"
    reply_markup = get_assets_menu_keyboard()
    if query:
        await query.answer()
        await query.edit_message_text(text=message_text, reply_markup=reply_markup)
    else:
        await update.message.reply_text(text=message_text, reply_markup=reply_markup)

async def asset_list_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    parts = query.data.split('_')
    prefix, status_key, offset_str = parts[0], parts[2], parts[3]
    search_term = context.user_data.get('asset_search_term') if 'search' in prefix else None

    status_map = {'all': None, 'rtd': 'ready to deploy', 'deployed': 'deployed'}
    status = status_map.get(status_key)
    offset = int(offset_str)
    assets_data = await get_assets(status=status, limit=LIMIT, offset=offset, search=search_term)

    if assets_data and 'rows' in assets_data:
        message_text = format_asset_list(assets_data)
        total = assets_data.get('total', 0)
        new_prefix = query.data.rsplit('_', 1)[0]
        reply_markup = get_paginator_keyboard(offset, total, LIMIT, new_prefix)
        await query.edit_message_text(text=message_text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
    else:
        await query.edit_message_text("Aktivlar topilmadi yoki yuklashda xatolik yuz berdi.")

async def view_asset_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        asset_id = int(context.args[0])
    except (IndexError, ValueError):
        await update.message.reply_text("Noto'g'ri format. Misol: /view_asset 123")
        return
    asset_data = await get_asset_by_id(asset_id)
    message_text = format_asset_details(asset_data)
    reply_markup = None
    if asset_data and not asset_data.get('assigned_to') and not ('status' in asset_data and asset_data['status'] == 'error'):
        reply_markup = get_asset_actions_keyboard(asset_id)
    await update.message.reply_html(message_text, reply_markup=reply_markup)

async def search_asset_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("🔍 Qidiruv uchun aktiv nomi, tegi yoki serial raqamini kiriting:",
                                 reply_markup=get_back_button('assets_menu'))
    return SEARCH

async def search_asset_receive(update: Update, context: ContextTypes.DEFAULT_TYPE):
    search_term = update.message.text
    context.user_data['asset_search_term'] = search_term
    assets_data = await get_assets(search=search_term, limit=LIMIT, offset=0)

    if assets_data and assets_data.get('total', 0) > 0:
        message_text = f"<b>'{search_term}' bo'yicha qidiruv natijalari:</b>\n\n" + format_asset_list(assets_data)
        reply_markup = get_paginator_keyboard(0, assets_data['total'], LIMIT, "assets_list_all")
        await update.message.reply_html(message_text, reply_markup=reply_markup)
    else:
        await update.message.reply_text(f"'{search_term}' bo'yicha hech narsa topilmadi.", reply_markup=get_assets_menu_keyboard())

    return ConversationHandler.END

async def add_asset_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data['new_asset'] = {}
    await query.edit_message_text("Yangi aktiv nomini kiriting:", reply_markup=get_back_button('assets_menu'))
    return ADD_NAME

async def add_asset_get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['new_asset']['name'] = update.message.text
    await update.message.reply_text("Aktiv uchun unikal Asset Tag kiriting:")
    return ADD_TAG

async def add_asset_get_tag(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['new_asset']['asset_tag'] = update.message.text
    models = await get_models() 
    
    reply_markup = format_selection_keyboard(models, 'model', 'assets_add')
    if reply_markup:
        await update.message.reply_text("Modelni tanlang:", reply_markup=reply_markup)
        return ADD_MODEL
    else:
        await update.message.reply_text("Modellar topilmadi. Aktiv yaratish bekor qilindi.", reply_markup=get_assets_menu_keyboard())
        return ConversationHandler.END

async def add_asset_get_model(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    model_id = query.data.split('_')[-1]
    context.user_data['new_asset']['model_id'] = int(model_id)
    statuses = await get_status_labels() 
    
    reply_markup = format_selection_keyboard(statuses, 'status', 'assets_add')
    if reply_markup:
        await query.edit_message_text("Statusni tanlang:", reply_markup=reply_markup)
        return ADD_STATUS
    else:
        await query.edit_message_text("Statuslar topilmadi. Aktiv yaratish bekor qilindi.", reply_markup=get_assets_menu_keyboard())
        return ConversationHandler.END

async def add_asset_get_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    status_id = query.data.split('_')[-1]
    context.user_data['new_asset']['status_id'] = int(status_id)

    payload = context.user_data['new_asset']
    result = await create_asset(payload) 

    if result and result.get('status') == 'success':
        message = "✅ Aktiv muvaffaqiyatli yaratildi!\n"
        asset_details = await get_asset_by_id(result['payload']['id']) 
        
        message += format_asset_details(asset_details)
        await query.edit_message_text(message, parse_mode=ParseMode.HTML, reply_markup=get_assets_menu_keyboard())
    else:
        await query.edit_message_text(f"❌ Xatolik: {result.get('messages', 'Noma\'lum xato')}", reply_markup=get_assets_menu_keyboard())

    context.user_data.clear()
    return ConversationHandler.END

async def assign_asset_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    asset_id = query.data.split('_')[-1]
    context.user_data['assign_asset_id'] = asset_id
    await query.edit_message_text("👤 Aktivni biriktirish uchun foydalanuvchi ismini yoki username'ini kiriting:",
                                 reply_markup=get_back_button('assets_menu'))
    return ASSIGN_USER

async def assign_asset_select_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    search_term = update.message.text
    users_data = await get_users(search=search_term, limit=5)

    if not users_data or not users_data.get('rows'):
        await update.message.reply_text("Bunday foydalanuvchi topilmadi. Qaytadan urinib ko'ring.", 
                                         reply_markup=get_back_button('assets_menu'))
        return ASSIGN_USER

    buttons = []
    asset_id = context.user_data['assign_asset_id']
    for user in users_data['rows']:
        callback_data = f"assign_confirm_{asset_id}_{user['id']}"
        buttons.append([InlineKeyboardButton(user['name'], callback_data=callback_data)])

    buttons.append([InlineKeyboardButton("⬅️ Orqaga", callback_data="assets_menu")])
    reply_markup = InlineKeyboardMarkup(buttons)
    await update.message.reply_text("Quyidagilardan birini tanlang:", reply_markup=reply_markup)

    return ConversationHandler.END

async def assign_asset_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    if query and query.data:
        await query.answer()
        try:
            _, asset_id, user_id = query.data.split('_')
            result = await assign_asset(asset_id, user_id)

            if result and result.get('status') == 'success':
                await query.edit_message_text(
                    f"✅ Muvaffaqiyatli biriktirildi!\n\n{result.get('messages')}",
                    reply_markup=get_assets_menu_keyboard()
                )
            else:
                await query.edit_message_text(
                    f"❌ Xatolik: {result.get('messages', 'Noma\'lum xato')}",
                    reply_markup=get_assets_menu_keyboard()
                )
        except ValueError:
            await query.edit_message_text(
                "❌ Xatolik: Callback query ma'lumotlari noto'g'ri formatda.",
                reply_markup=get_assets_menu_keyboard()
            )
    else:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="❌ Xatolik: Callback query mavjud emas yoki noto'g'ri.",
            reply_markup=get_assets_menu_keyboard()
        )

    context.user_data.clear()