
from db import is_user_registered, add_user
import datetime

import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes, ConversationHandler
from datetime import datetime, date, timedelta
import re
import sqlite3
import logging
import re
from datetime import date, timedelta, datetime
import sqlite3
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

REGISTER, INPUT_PASSWORD, INPUT_NAME, INPUT_PHONE, INPUT_COMPANY, INPUT_EMAIL, MAIN_MENU, ORDER_VEHICLE, CONFIRM_ORDER = range(9)
VALID_PASSWORD = "123"
DB_PATH = 'requests.db'
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("Команда /start вызвана")
    user_id = update.message.from_user.id
    if is_user_registered(user_id):
        await show_main_menu(update, context)
        return MAIN_MENU
    else:
        await update.message.reply_text("Привет! Нажмите /register для регистрации.")
        return REGISTER

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
        [InlineKeyboardButton("vopros", callback_data='vopros')],
        [InlineKeyboardButton("Изменить регистрационные данные", callback_data='edit_register_info')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    if update.message:
        await update.message.reply_text(
            text='Добро пожаловать на Винзавод - выберите кнопку ниже',
            reply_markup=reply_markup
        )
    else:
        await update.callback_query.message.edit_text(
            text='Добро пожаловать на Винзавод - выберите кнопку ниже',
            reply_markup=reply_markup
        )
    return MAIN_MENU


async def handle_vopros(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обрабатывает нажатие кнопки и задает вопрос."""
    query = update.callback_query
    await query.answer()  # Подтверждение нажатия кнопки

    await query.edit_message_text(
        text='Введите номер авто в формате X777XX77:'
    )
    return ORDER_VEHICLE


async def order_vehicle(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.callback_query.message.edit_text('Введите номер авто в формате X777XX77:')
    return ORDER_VEHICLE

async def input_vehicle_brand(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if not re.match(r'^[A-ZА-Я]\d{3}[A-ZА-Я]{2}\d{2,3}$', update.message.text):
        await update.message.reply_text('Неправильный формат номера автомобиля. Попробуйте снова.')
        return ORDER_VEHICLE
    context.user_data['vehicle_number'] = update.message.text
    await update.message.reply_text('Введите марку авто:')
    return ORDER_VEHICLE

async def input_guest_status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['vehicle_brand'] = update.message.text
    keyboard = [
        [InlineKeyboardButton("Гость", callback_data='guest_yes')],
        [InlineKeyboardButton("Разгрузка", callback_data='guest_no')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Гость или Разгрузка?', reply_markup=reply_markup)
    return ORDER_VEHICLE

async def input_request_date(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    context.user_data['is_guest'] = 'Гость' if query.data == 'guest_yes' else 'Разгрузка'
    keyboard = [
        [InlineKeyboardButton("Сегодня", callback_data='today')],
        [InlineKeyboardButton("Завтра", callback_data='tomorrow')],
        [InlineKeyboardButton("Послезавтра", callback_data='day_after_tomorrow')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.message.edit_text('На какое число?', reply_markup=reply_markup)
    return ORDER_VEHICLE

async def confirm_request(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    request_date = query.data
    today = date.today()
    if request_date == 'today':
        context.user_data['request_date'] = today
    elif request_date == 'tomorrow':
        context.user_data['request_date'] = today + timedelta(days=1)
    elif request_date == 'day_after_tomorrow':
        context.user_data['request_date'] = today + timedelta(days=2)

    user_data = context.user_data
    await query.edit_message_text(
        text=f"Заявка подтверждена. Данные:\n"
             f"Номер авто: {user_data['vehicle_number']}\n"
             f"Марка авто: {user_data['vehicle_brand']}\n"
             f"Статус: {user_data['is_guest']}\n"
             f"Дата: {user_data['request_date']}"
    )

    logger.info(f"Заявка от пользователя {update.effective_user.id} внесена в базу данных")

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
