# telegram_bot.py
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackContext, CallbackQueryHandler, filters, MessageHandler
import logging
import requests
from bs4 import BeautifulSoup

# Функция для получения данных с веб-страницы
def get_olympiad_links():
    url = 'https://postypashki.ru/ecwd_calendar/calendar/?date=2024-3&t=full/%D0%BE%D0%BB%D0%B8%D0%BC%D0%BF%D0%B8%D0%B0%D0%B4%D1%8B/'
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        olympiad_links = soup.find_all('a', href=True)
        olympiad_data = []
        for link in olympiad_links:
            if '/event/' in link['href']:
                olympiad_data.append(link['href'])
        return olympiad_data
    else:
        return None

def get_olympiad_info():
    urls = get_olympiad_links()
    returned_data = []
    for url in urls:
        dictt = dict()
        dictt["url"] = url
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            olympiad_info = soup.find_all('h1')
            olympiad_titles = [info.text for info in olympiad_info]
            dictt["name"] = olympiad_titles[0]
            olympiad_dates = soup.find_all('span', class_="ecwd-event-date")
            olympiad_date = [info.text for info in olympiad_dates]
            dictt["date"] = olympiad_date[0].split()[0] + " " + olympiad_date[0].split()[1] + olympiad_date[0].split()[2] + olympiad_date[0].split()[3]
            returned_data.append(dictt)
    return returned_data

# Обработчик команды /info
async def get_info(update: Update, context: CallbackContext) -> None:
    info = get_olympiad_info()
    sent_olympiads = context.chat_data.get('sent_olympiads', {})

    for data in info:
        if data['name'] not in sent_olympiads:
            if update.message:  # Проверяем, существует ли update.message
                await update.message.reply_text(f'Название олимпиады: {data["name"]}, Дата: {data["date"]}')
            else:  # Если update.message отсутствует, используем update.callback_query.message
                await update.callback_query.message.reply_text(f'Название олимпиады: {data["name"]}, Дата: {data["date"]}')
            sent_olympiads[data['name']] = True
            context.chat_data['sent_olympiads'] = sent_olympiads

async def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    if query.data == 'info':
        await get_info(update, context)
    elif query.data == 'register':
        if update.message:
            await update.message.reply_text('Для регистрации на сайте, пожалуйста, введите ваше имя и email в формате: Имя Email')
        else:
            await update.effective_chat.send_message('Для регистрации на сайте, пожалуйста, введите ваше имя и email в формате: Имя Email')
    elif query.data == 'login':
        if query.message:
            await query.message.reply_text('Для входа введите ваше имя и email, которые вы использовали при регистрации.')
        else:
            await update.effective_chat.send_message('Для входа введите ваше имя и email, которые вы использовали при регистрации.')
    elif query.data == 'month_selection':
        await show_month_selection(update, context)
    elif query.data.startswith('days_'):
        await handle_notification_days_selection(update, context)

async def show_month_selection(update: Update, context: CallbackContext) -> None:
    keyboard = [
        [InlineKeyboardButton("Январь", callback_data='month_01')],
        [InlineKeyboardButton("Февраль", callback_data='month_02')],
        [InlineKeyboardButton("Март", callback_data='month_03')],
        [InlineKeyboardButton("Апрель", callback_data='month_04')],
        [InlineKeyboardButton("Май", callback_data='month_05')],
        [InlineKeyboardButton("Июнь", callback_data='month_06')],
        [InlineKeyboardButton("Июлю", callback_data='month_07')],
        [InlineKeyboardButton("Август", callback_data='month_08')],
        [InlineKeyboardButton("Сентябрь", callback_data='month_09')],
        [InlineKeyboardButton("Октябрь", callback_data='month_10')],
        [InlineKeyboardButton("Ноябрь", callback_data='month_11')],
        [InlineKeyboardButton("Декабрь", callback_data='month_12')],

    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    if update.message:
        await update.message.reply_text('Выберите месяц:', reply_markup=reply_markup)
    else:
        await update.callback_query.message.reply_text('Выберите месяц:', reply_markup=reply_markup)

async def start(update: Update, context: CallbackContext) -> None:
    keyboard = [
        [InlineKeyboardButton("Информация о олимпиадах", callback_data='info')],
        [InlineKeyboardButton("Регистрация", callback_data='register')],
        [InlineKeyboardButton("Вход", callback_data='login')],
        [InlineKeyboardButton("Выбрать месяц", callback_data='month_selection')],
        [InlineKeyboardButton("За 7 дней", callback_data='days_7'),
         InlineKeyboardButton("За 14 дней", callback_data='days_14'),
         InlineKeyboardButton("За 30 дней", callback_data='days_30')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Выберите действие:', reply_markup=reply_markup)

def error_handler(update: Update, context: CallbackContext) -> None:
    logger.error(f'Update {update} caused error {context.error}')

# Обработчик команды /register
async def register(update: Update, context: CallbackContext) -> None:
    if update.message:  # Проверяем, существует ли update.message
        await update.message.reply_text('Для регистрации на сайте, пожалуйста, введите ваше имя, номер телефона и email в формате: Имя Номер_телефона Email')
    else:
        await update.effective_chat.send_message('Для регистрации на сайте, пожалуйста, введите ваше имя, номер телефона и email в формате: Имя Номер_телефона Email')

# Обработчик команды /login
async def login(update: Update, context: CallbackContext) -> None:
    if update.message:  # Проверяем, существует ли update.message
        await update.message.reply_text('Для входа введите ваше имя, номер телефона и email, которые вы использовали при регистрации в формате: Имя Номер_телефона Email')
    else:
        await update.effective_chat.send_message('Для входа введите ваше имя, номер телефона и email, которые вы использовали при регистрации в формате: Имя Номер_телефона Email')

# Обработчик текстовых сообщений для регистрации
async def handle_registration(update: Update, context: CallbackContext) -> None:
    user_input = update.message.text
    parts = user_input.split()
    if len(parts) == 3:
        name, phone, email = parts
        # Регистрируем пользователя в боте
        user_data = context.chat_data.get('users', {})
        user_data[update.effective_user.id] = {'name': name, 'phone': phone, 'email': email}
        context.chat_data['users'] = user_data

        await update.message.reply_text('Вы успешно зарегистрированы!')
    else:
        await update.message.reply_text('Неверный формат. Пожалуйста, введите имя, номер телефона и email через пробел.')

# Обработчик текстовых сообщений для входа
async def handle_login(update: Update, context: CallbackContext) -> None:
    user_input = update.message.text
    parts = user_input.split()
    if len(parts) == 3:
        name, phone, email = parts
        # Проверяем, существует ли пользователь в базе данных
        user_data = context.chat_data.get('users', {})
        if update.effective_user.id in user_data and user_data[update.effective_user.id]['name'] == name and user_data[update.effective_user.id]['phone'] == phone and user_data[update.effective_user.id]['email'] == email:
            await update.message.reply_text('Вы успешно вошли!')
        else:
            await update.message.reply_text('Неверные данные для входа. Пожалуйста, попробуйте еще раз.')
    else:
        await update.message.reply_text('Неверный формат. Пожалуйста, введите имя, номер телефона и email через пробел.')

async def handle_notification_days_selection(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    selected_days = int(query.data.split('_')[1])  # Извлекаем число из callback_data
    context.chat_data['notification_days'] = selected_days
    await query.edit_message_text(text=f'Уведомления будут отправляться за {selected_days} дней до олимпиады.')

async def send_notifications(context: CallbackContext) -> None:
    n_days_before = context.chat_data.get('notification_days', 7)  # Значение по умолчанию - 7 дней
    current_date = datetime.datetime.now()
    olympiad_info = get_olympiad_info()
    users = context.chat_data.get('users', {})

    for data in olympiad_info:
        event_date = datetime.datetime.strptime(data['date'], '%d %B %Y')
        if (event_date - current_date).days == n_days_before:
            for user_id, user_info in users.items():
                await context.bot.send_message(
                    chat_id=user_id,
                    text=f'Ближайшая олимпиада: {data["name"]}, Дата: {data["date"]}\nСсылка для регистрации: {data["url"]}'
                )
# Основная функция запуска бота
def main() -> None:
    token = '7311756717:AAFMfLoYeWwxaq6Ip3bTHDwtxU9J7sf0MvY'
    application = Application.builder().token(token).build()

    application.add_handler(CommandHandler('start', start))
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_registration))
    application.add_handler(CommandHandler('login', login))
    application.add_error_handler(error_handler)

    job_queue = application.job_queue
    job_queue.run_repeating(send_notifications, interval=86400, first=0)  # Запуск каждые 24 часа

    application.run_polling()


if __name__ == '__main__':
    main()