from telegram import Update, ReplyKeyboardRemove
from telegram.ext import ContextTypes, ConversationHandler
from keyboards.menus import get_main_menu_keyboard

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if update.message:
        await update.message.reply_html(
            f"Salom, {user.mention_html()}!\n\nSnipe-IT boshqaruv botiga xush kelibsiz.",
            reply_markup=get_main_menu_keyboard()
        )
    else:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"Salom, {user.mention_html()}!\n\nSnipe-IT boshqaruv botiga xush kelibsiz.",
            reply_markup=get_main_menu_keyboard()
        )
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Suhbatni (Conversation) bekor qilish"""
    query = update.callback_query
    message = "Amal bekor qilindi."
    if query:
        await query.answer()
        await query.edit_message_text(text=message)
    else:
        await update.message.reply_text(text=message, reply_markup=ReplyKeyboardRemove())
    context.user_data.clear()
    return ConversationHandler.END
