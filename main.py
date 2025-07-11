from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ConversationHandler, filters
from config import TELEGRAM_BOT_TOKEN
from handlers import assets, users, common
import re
import pytz


def main():
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # === Conversation Handlerlar ===
    asset_add_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(assets.add_asset_start, pattern='^assets_add_start$')],
        states={
            assets.ADD_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, assets.add_asset_get_name)],
            assets.ADD_TAG: [MessageHandler(filters.TEXT & ~filters.COMMAND, assets.add_asset_get_tag)],
            assets.ADD_MODEL: [CallbackQueryHandler(assets.add_asset_get_model, pattern='^assets_add_model_')],
            assets.ADD_STATUS: [CallbackQueryHandler(assets.add_asset_get_status, pattern='^assets_add_status_')]
        },
        fallbacks=[CommandHandler('cancel', common.cancel), CallbackQueryHandler(assets.assets_menu, pattern='^assets_menu$')],
        conversation_timeout=300
    )

    asset_search_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(assets.search_asset_start, pattern='^assets_search_start$')],
        states={
            assets.SEARCH: [MessageHandler(filters.TEXT & ~filters.COMMAND, assets.search_asset_receive)],
        },
        fallbacks=[CommandHandler('cancel', common.cancel), CallbackQueryHandler(assets.assets_menu, pattern='^assets_menu$')]
    )

    asset_assign_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(assets.assign_asset_start, pattern='^asset_assign_start_')],
        states={
            assets.ASSIGN_USER: [MessageHandler(filters.TEXT & ~filters.COMMAND, assets.assign_asset_select_user)]
        },
        fallbacks=[CommandHandler('cancel', common.cancel), CallbackQueryHandler(assets.assets_menu, pattern='^assets_menu$')]
    )

    user_add_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(users.add_user_start, pattern='^users_add_start$')],
        states={
            users.ADD_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, users.add_user_get_name)],
            users.ADD_USERNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, users.add_user_get_username)],
            users.ADD_PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, users.add_user_get_password)],
        },
        fallbacks=[CommandHandler('cancel', common.cancel), CallbackQueryHandler(users.users_menu, pattern='^users_menu$')]
    )

    user_search_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(users.search_user_start, pattern='^users_search_start$')],
        states={
            users.SEARCH: [MessageHandler(filters.TEXT & ~filters.COMMAND, users.search_user_receive)],
        },
        fallbacks=[CommandHandler('cancel', common.cancel), CallbackQueryHandler(users.users_menu, pattern='^users_menu$')]
    )

    # === Handlerlar qo‘shiladi ===
    app.add_handler(CommandHandler("start", common.start))
    app.add_handler(asset_add_handler)
    app.add_handler(asset_search_handler)
    app.add_handler(asset_assign_handler)
    app.add_handler(user_add_handler)
    app.add_handler(user_search_handler)

    # Matnli menyu
    app.add_handler(MessageHandler(filters.Regex(r'^🗄 Aktivlar \(Assets\)$'), assets.assets_menu))
    app.add_handler(MessageHandler(filters.Regex(r'^👥 Foydalanuvchilar \(Users\)$'), users.users_menu))

    # Inline tugmalar
    app.add_handler(CallbackQueryHandler(assets.assets_menu, pattern='^assets_menu$'))
    app.add_handler(CallbackQueryHandler(users.users_menu, pattern='^users_menu$'))
    app.add_handler(CallbackQueryHandler(assets.asset_list_callback, pattern='^assets_list_'))
    app.add_handler(CallbackQueryHandler(users.user_list_callback, pattern='^users_list_'))
    app.add_handler(CallbackQueryHandler(assets.assign_asset_confirm, pattern='^assign_confirm_'))

    # /view_asset_123 yoki /view_user_45 kabi buyruqlar uchun ASINXRON handlerlar
    
    # "def" o'rniga "async def" dan foydalanamiz
    async def asset_redirect(update, context):
        match = re.search(r'/view_asset_(\d+)', update.message.text)
        if match:
            context.args = [match.group(1)]
            # Asinxron funksiyani await qilamiz
            await assets.view_asset_command(update, context)

    # "def" o'rniga "async def" dan foydalanamiz
    async def user_redirect(update, context):
        match = re.search(r'/view_user_(\d+)', update.message.text)
        if match:
            context.args = [match.group(1)]
            # Asinxron funksiyani await qilamiz
            await users.view_user_command(update, context)

    app.add_handler(MessageHandler(filters.Regex(r'^/view_asset_'), asset_redirect))
    app.add_handler(MessageHandler(filters.Regex(r'^/view_user_'), user_redirect))

    print("✅ Bot ishga tushdi...")
    app.run_polling()

if __name__ == '__main__':
    main()