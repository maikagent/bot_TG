
from db import is_user_registered, add_user, add_request
import datetime
import logging
from telegram.ext import ContextTypes, ConversationHandler
import re
from datetime import date, timedelta, datetime
import sqlite3
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackContext


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

REGISTER, INPUT_PASSWORD, INPUT_NAME, INPUT_PHONE, INPUT_COMPANY, INPUT_EMAIL, MAIN_MENU, INPUT_VEHICLE_BRAND, ORDER_VEHICLE, CONFIRM_ORDER, INPUT_VEHICLE_PURPOSE = range(11)
VALID_PASSWORD = "123"
DB_PATH = 'requests.db'



async def register(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if is_user_registered(user_id):
        await show_main_menu(update, context)
        return MAIN_MENU
    else:
        await update.message.reply_text('Введите пароль для регистрации:')
        return INPUT_PASSWORD

async def input_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == VALID_PASSWORD:
        await update.message.reply_text('Пароль верный. Введите ваше имя:')
        return INPUT_NAME
    else:
        await update.message.reply_text('Пароль неверный. Попробуйте еще раз:')
        return INPUT_PASSWORD

async def input_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['user_id'] = update.message.from_user.id
    context.user_data['name'] = update.message.text
    await update.message.reply_text('Введите ваш номер телефона:')
    return INPUT_PHONE

async def input_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['phone'] = update.message.text
    await update.message.reply_text('Введите вашу компанию:')
    return INPUT_COMPANY

async def input_company(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['company'] = update.message.text
    await update.message.reply_text('Введите ваш email:')
    return INPUT_EMAIL

async def input_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['email'] = update.message.text
    user_id = context.user_data['user_id']
    name = context.user_data['name']
    phone = context.user_data['phone']
    company = context.user_data['company']
    email = context.user_data['email']
    if not is_user_registered(user_id):
        add_user(user_id, name, phone, company, email)
    await show_main_menu(update, context)
    return MAIN_MENU

async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Заказать пропуск на авто", callback_data='order_vehicle')],
        [InlineKeyboardButton("Вопрос", callback_data='question')],
        [InlineKeyboardButton("Изменить регистрационные данные", callback_data='edit_register_info')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    if update.message:
        await update.message.reply_text(
            text='Добро пожаловать на Винзавод - выберите кнопку ниже',
            reply_markup=reply_markup
        )
    else:
        await update.callback_query.message.reply_text(
            text='Добро пожаловать на Винзавод - выберите кнопку ниже',
            reply_markup=reply_markup
        )
    return MAIN_MENU

async def order_vehicle(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.callback_query.message.reply_text('Введите номер авто в формате X777XX77:')
    return INPUT_VEHICLE_BRAND

async def input_vehicle_brand(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if not re.match(r'^[A-ZА-Я]\d{3}[A-ZА-Я]{2}\d{2,3}$', update.message.text):
        await update.message.reply_text('Неправильный формат номера автомобиля. Попробуйте снова.')
        return INPUT_VEHICLE_BRAND

    context.user_data['vehicle_number'] = update.message.text
    await update.message.reply_text('Введите марку авто:')
    return ORDER_VEHICLE

async def order_vehicle_brand(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['vehicle_brand'] = update.message.text
    await update.message.reply_text('Введите цель заезда (Гость, Разгрузка):')
    return INPUT_VEHICLE_PURPOSE

async def input_vehicle_purpose(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['vehicle_purpose'] = update.message.text
    summary = (
        f"Номер авто: {context.user_data['vehicle_number']}\n"
        f"Марка авто: {context.user_data['vehicle_brand']}\n"
        f"Цель заезда: {context.user_data['vehicle_purpose']}\n"
        "Всё верно?"
    )
    keyboard = [
        [InlineKeyboardButton("Да", callback_data='confirm')],
        [InlineKeyboardButton("Нет", callback_data='cancel')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(summary, reply_markup=reply_markup)
    return CONFIRM_ORDER


async def confirm_order(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()  # Подтверждаем получение callback-запроса

    if query.data == 'confirm':
        user_id = update.effective_user.id
        vehicle_number = context.user_data['vehicle_number']
        vehicle_brand = context.user_data['vehicle_brand']
        is_guest = context.user_data.get('is_guest', False)  # или другое значение по умолчанию
        request_date = datetime.now()  # Или возьмите дату из ответа пользователя

        # Вставляем данные в базу данных
        add_request(user_id, vehicle_number, vehicle_brand, is_guest, request_date)

        await query.edit_message_text(text="Запрос принят и записан в базу данных.")
    else:
        await query.edit_message_text(text="Запрос был отменен.")

    return ConversationHandler.END  # Завершаем разговор

async def cancel_order(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.callback_query.message.reply_text('Введите /start для возврата в главное меню')
    return MAIN_MENU

    # Добавьте запрос на сохранение в базу данных здесь
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()
    cursor.execute('''
        INSERT INTO requests (user_id, vehicle_number, vehicle_brand, is_guest, request_date, submission_date)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (update.effective_user.id, user_data['vehicle_number'], user_data['vehicle_brand'], user_data['is_guest'], user_data['request_date'], datetime.now()))
    connection.commit()
    connection.close()

    return ConversationHandler.END
