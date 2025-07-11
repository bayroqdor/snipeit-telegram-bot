from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def get_paginator_keyboard(current_offset, total_items, limit, callback_prefix):
    buttons = []
    row = []
    if current_offset > 0:
        prev_offset = max(0, current_offset - limit)
        row.append(InlineKeyboardButton("⬅️ Orqaga", callback_data=f"{callback_prefix}_{prev_offset}"))
    if current_offset + limit < total_items:
        next_offset = current_offset + limit
        row.append(InlineKeyboardButton("Oldinga ➡️", callback_data=f"{callback_prefix}_{next_offset}"))
    if row:
        buttons.append(row)
    return InlineKeyboardMarkup(buttons) if buttons else None