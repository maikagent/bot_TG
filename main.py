import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, ConversationHandler, filters, ContextTypes
)
from handlers import (
    register, input_password, input_name,
    input_phone, input_company, input_email, show_main_menu,
    input_vehicle_brand, order_vehicle, INPUT_VEHICLE_BRAND,
    MAIN_MENU, ORDER_VEHICLE, REGISTER, INPUT_PASSWORD,
    INPUT_NAME, INPUT_PHONE, INPUT_COMPANY, INPUT_EMAIL,
    input_vehicle_purpose, confirm_order, cancel_order,
    INPUT_VEHICLE_PURPOSE, CONFIRM_ORDER, order_vehicle_brand
)
from db import init_db, is_user_registered, add_user

# Логирование для отладки
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Состояния для ConversationHandler
# REGISTER, INPUT_PASSWORD, INPUT_NAME, INPUT_PHONE, INPUT_COMPANY, INPUT_EMAIL, MAIN_MENU, ORDER_VEHICLE, CONFIRM_ORDER, INPUT_VEHICLE_BRAND = range(10)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if is_user_registered(user_id):
        await show_main_menu(update, context)
        return MAIN_MENU
    else:
        await update.message.reply_text("Привет! Нажмите /register для регистрации.")
        return REGISTER

def main() -> None:
    application = Application.builder().token("7364780446:AAFHddC3AfzoG-1SI8-hfwTWKZjuc8YWZ6A").build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start_command)],
        states={
            REGISTER: [CommandHandler('register', register)],
            INPUT_PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, input_password)],
            INPUT_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, input_name)],
            INPUT_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, input_phone)],
            INPUT_COMPANY: [MessageHandler(filters.TEXT & ~filters.COMMAND, input_company)],
            INPUT_EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, input_email)],
            MAIN_MENU: [CallbackQueryHandler(order_vehicle, pattern='order_vehicle')],
            INPUT_VEHICLE_BRAND: [MessageHandler(filters.TEXT & ~filters.COMMAND, input_vehicle_brand)],
            ORDER_VEHICLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, order_vehicle_brand)],
            INPUT_VEHICLE_PURPOSE: [MessageHandler(filters.TEXT & ~filters.COMMAND, input_vehicle_purpose)],
            CONFIRM_ORDER: [
                CallbackQueryHandler(confirm_order, pattern='confirm'),
                CallbackQueryHandler(cancel_order, pattern='cancel')
            ]
        },
        fallbacks=[CommandHandler('start', start_command)]
    )

    application.add_handler(conv_handler)
    init_db()
    application.run_polling()

if __name__ == '__main__':
    main()
