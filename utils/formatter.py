from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def format_asset_list(assets_data):
    if not assets_data or 'rows' not in assets_data or not assets_data['rows']:
        return "Aktivlar topilmadi."
    message = ""
    for asset in assets_data['rows']:
        asset_id = asset.get('id')
        asset_name = asset.get('name', 'Nomsiz')
        asset_tag = asset.get('asset_tag')
        message += f"🔹 {asset_name} (Tag: {asset_tag}) - /view_asset_{asset_id}\n"
    return message

def format_asset_details(asset_data):
    if not asset_data or 'status' in asset_data and asset_data['status'] == 'error':
        return f"Aktiv haqida ma'lumot topilmadi.\nXato: {asset_data.get('messages', 'Noma\'lum')}"
    name = asset_data.get('name', 'N/A')
    tag = asset_data.get('asset_tag', 'N/A')
    serial = asset_data.get('serial', 'N/A')
    model = asset_data.get('model', {}).get('name', 'N/A')
    status = asset_data.get('status_label', {}).get('name', 'N/A')
    message = f"<b>Asset Details:</b>\n\n" \
              f"<b>Nomi:</b> {name}\n" \
              f"<b>Asset Tag:</b> {tag}\n" \
              f"<b>Serial raqami:</b> {serial}\n" \
              f"<b>Modeli:</b> {model}\n" \
              f"<b>Holati:</b> {status}\n\n"
    assigned_to = asset_data.get('assigned_to')
    if assigned_to:
        user_name = assigned_to.get('name', 'Noma\'lum foydalanuvchi')
        datetime_str = asset_data.get('last_checkout', {}).get('datetime')
        checkout_date = datetime_str.split(' ')[0] if datetime_str else 'N/A'
        message += f"👤 <b>Biriktirilgan:</b> {user_name}\n" \
                   f"🗓 <b>Berilgan sana:</b> {checkout_date}"
    else:
        message += "Bu aktiv hech kimga biriktirilmagan."
    return message

def format_user_list(users_data):
    if not users_data or 'rows' not in users_data or not users_data['rows']:
        return "Foydalanuvchilar topilmadi."
    message = ""
    for user in users_data['rows']:
        user_id = user.get('id')
        user_name = user.get('name', 'Nomsiz')
        message += f"👤 {user_name} - /view_user_{user_id}\n"
    return message

def format_user_details(user_data, user_assets):
    if not user_data or 'status' in user_data and user_data['status'] == 'error':
        return f"Foydalanuvchi topilmadi.\nXato: {user_data.get('messages', 'Noma\'lum')}"
    name = user_data.get('name', 'N/A')
    username = user_data.get('username', 'N/A')
    assets_count = user_data.get('assets_count', 0)
    message = f"<b>Foydalanuvchi ma'lumotlari:</b>\n\n" \
              f"<b>To'liq ismi:</b> {name}\n" \
              f"<b>Username:</b> {username}\n" \
              f"<b>Aktivlar soni:</b> {assets_count}\n\n"
    if user_assets and 'rows' in user_assets and user_assets['rows']:
        message += "<b>Biriktirilgan aktivlar:</b>\n"
        for asset in user_assets['rows']:
            asset_name = asset.get('name', 'Nomsiz')
            asset_tag = asset.get('asset_tag')
            message += f"🔹 {asset_name} (Tag: {asset_tag}) - /view_asset_{asset.get('id')}\n"
    else:
        message += "Bu foydalanuvchiga aktivlar biriktirilmagan."
    return message

def format_paginated_list(items, item_type):
    if not items or 'rows' not in items or not items['rows']:
        return None, "Ma'lumotlar topilmadi."
    buttons = []
    for item in items['rows']:
        callback_data = f"add_asset_{item_type}_{item['id']}"
        buttons.append([f"{item['name']}"])
    return "\n".join([row[0] for row in buttons]), "Kerakli elementni tanlang:"

def format_selection_keyboard(items, item_type, callback_prefix):
    if not items or 'rows' not in items or not items['rows']:
        return None
    buttons = []
    for item in items['rows']:
        callback_data = f"{callback_prefix}_{item_type}_{item['id']}"
        buttons.append([InlineKeyboardButton(item['name'], callback_data=callback_data)])
    return InlineKeyboardMarkup(buttons)
