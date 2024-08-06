import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, ConversationHandler, filters, ContextTypes
)
from handlers import (
    start, register, input_password, input_name,
    input_phone, input_company, input_email, show_main_menu,
    input_vehicle_brand, input_guest_status, input_request_date,
    confirm_request, handle_vopros, order_vehicle
)
from db import init_db, is_user_registered, add_user

# Логирование для отладки
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Состояния для ConversationHandler
REGISTER, INPUT_PASSWORD, INPUT_NAME, INPUT_PHONE, INPUT_COMPANY, INPUT_EMAIL, MAIN_MENU, ORDER_VEHICLE, CONFIRM_ORDER = range(9)

# Проверка регистрации в стартовой функции
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if is_user_registered(user_id):
        await show_main_menu(update, context)
        return MAIN_MENU
    else:
        await update.message.reply_text("Привет! Нажмите /register для регистрации.")
        return REGISTER

def main() -> None:
    application = Application.builder().token("7364780446:AAFHddC3AfzoG-1SI8-hfwTWKZjuc8YWZ6A").build()

    conversation_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            MAIN_MENU: [
                CallbackQueryHandler(order_vehicle, pattern='ORDER_VEHICLE'),
                CallbackQueryHandler(handle_vopros, pattern='vopros')
            ],
            ORDER_VEHICLE: [
                CallbackQueryHandler(order_vehicle, pattern='order_vehicle'),
                MessageHandler(filters.TEXT & ~filters.COMMAND, input_vehicle_brand),
                CallbackQueryHandler(input_guest_status, pattern='guest_.+'),
                CallbackQueryHandler(input_request_date, pattern='(today|tomorrow|day_after_tomorrow)'),
                CallbackQueryHandler(confirm_request, pattern='confirm_.+')
            ],
        },
        fallbacks=[CommandHandler('start', start)],
    )

    application.add_handler(conversation_handler)
    init_db()
    application.run_polling()

if __name__ == '__main__':
    main()
