# telegram_bot.py
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackContext, CallbackQueryHandler, filters, MessageHandler
import logging
import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import datetime


# Настройка логирования


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
            # Парсинг даты должен быть корректным и соответствовать ожидаемому формату
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

    # Добавляем кнопку оповещения после отправки информации
    keyboard = [
        [InlineKeyboardButton("За 7 дней", callback_data='days_7'),
         InlineKeyboardButton("За 14 дней", callback_data='days_14'),
         InlineKeyboardButton("За 30 дней", callback_data='days_30')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    if update.message:
        await update.message.reply_text('Выберите, когда получать уведомления:', reply_markup=reply_markup)
    elif update.callback_query and update.callback_query.message:
        await update.callback_query.message.reply_text('Выберите, когда получать уведомления:', reply_markup=reply_markup)

# Обработчик команды /register
async def register(update: Update, context: CallbackContext) -> None:
    if update.message:  # Проверяем, существует ли update.message
        await update.message.reply_text('Для регистрации на сайте, пожалуйста, введите ваше имя, номер телефона и email в формате: Имя Номер_телефона Email')
    else:
        await update.effective_chat.send_message('Для регистрации на сайте, пожалуйста, введите ваше имя, номер телефона и email в формате: Имя Номер_телефона Email')

SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
SMTP_USERNAME = 'khulagovinfo69@gmail.com'
SMTP_PASSWORD ='qgen kjkk nrwf nsrr'
EMAIL_FROM = 'khulagovinfo69@gmail.com'

def send_email(to_email, subject, message):
    msg = MIMEMultipart()
    msg['From'] = EMAIL_FROM
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(message, 'plain'))

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        text = msg.as_string()
        server.sendmail(EMAIL_FROM, to_email, text)
        server.quit()
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")


users = {}


def error_handler(update: Update, context: CallbackContext) -> None:
    logger.error(f'Update {update} caused error {context.error}')
async def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    if query.data == 'info':
        await get_info(update, context)
    elif query.data == 'register':
        if update.message:
            await update.message.reply_text('Для регистрации на сайте, пожалуйста, введите ваше имя, номер телефона и email в формате: Имя Номер_телефона Email')
        else:
            await update.effective_chat.send_message('Для регистрации на сайте, пожалуйста, введите ваше имя, номер телефона и email в формате: Имя Номер_телефона Email')
    elif query.data == 'login':
        await login(update, context)  # Вызываем функцию login для кнопки "Вход"
    elif query.data.startswith('days_'):
        await handle_notification_days_selection(update, context)

# Измените функцию `start` для включения кнопки выбора месяца
async def start(update: Update, context: CallbackContext) -> None:
    keyboard = [
        [InlineKeyboardButton("Информация о олимпиадах", callback_data='info')],
        [InlineKeyboardButton("Регистрация", callback_data='register')],
        [InlineKeyboardButton("Вход", callback_data='login')],
        [InlineKeyboardButton("За 7 дней", callback_data='days_7'),
         InlineKeyboardButton("За 14 дней", callback_data='days_14'),
         InlineKeyboardButton("За 30 дней", callback_data='days_30')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Выберите действие:', reply_markup=reply_markup)

# Обработчик нажатий на кнопки
async def send_notifications(context: CallbackContext) -> None:
    n_days_before = context.chat_data.get('notification_days', 7)  # Значение по умолчанию - 7 дней
    current_date = datetime.datetime.now()
    olympiad_info = get_olympiad_info()
    users = context.chat_data.get('users', {})

    for data in olympiad_info:
        # Парсинг даты должен быть корректным и соответствовать ожидаемому формату
        event_date = datetime.datetime.strptime(data['date'], '%d %B %Y')
        if (event_date - current_date).days == n_days_before:
            for user_id, user_info in users.items():
                await context.bot.send_message(
                    chat_id=user_id,
                    text=f'Ближайшая олимпиада: {data["name"]}, Дата: {data["date"]}\nСсылка для регистрации: {data["url"]}'
                )



async def handle_notification_days_selection(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    selected_days = int(query.data.split('_')[1])  # Извлекаем число из callback_data
    if selected_days in [7, 14, 30]:  # Проверяем, что выбранное количество дней корректно
        context.chat_data['notification_days'] = selected_days
        await query.edit_message_text(text=f'Уведомления будут отправляться за {selected_days} дней до олимпиады.')
    else:
        await query.edit_message_text(text='Неверный выбор. Пожалуйста, выберите количество дней из предложенных вариантов.')



# Обработчик текстовых сообщений для регистрации


# Обработчик текстовых сообщений для регистрации
async def handle_registration(update: Update, context: CallbackContext) -> None:
    user_input = update.message.text
    parts = user_input.split()
    if len(parts) == 3:
        name, phone, email = parts
        # Регистрируем пользователя в боте
        user_data = (update.effective_user.id, name, phone, email)
        users[update.effective_user.id] = user_data
        await update.message.reply_text('Вы успешно зарегистрированы!')
        send_email(email, 'Успешная регистрация', f'Здравствуйте, {name}! Вы успешно зарегистрировались в нашем боте.')
    else:
        await update.message.reply_text('Неверный формат. Пожалуйста, введите имя, номер телефона и email через пробел.')


# Обработчик команды /login

# Обработчик команды /logiл
async def login(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    if user_id not in users:
        if update.callback_query:
            await update.callback_query.message.reply_text(
                'Вы должны сначала зарегистрироваться. Используйте команду /register.')
        else:
            await update.message.reply_text('Вы должны сначала зарегистрироваться. Используйте команду /register.')
        return

    if update.message:  # Проверяем, существует ли update.message
        await update.message.reply_text(
            'Для входа введите ваше имя, номер телефона и email, которые вы использовали при регистрации в формате: Имя Номер_телефона Email')
    else:
        await update.callback_query.message.reply_text(
            'Для входа введите ваше имя, номер телефона и email, которые вы использовали при регистрации в формате: Имя Номер_телефона Email')

# Обработчик текстовых сообщений для входа
async def handle_login(update: Update, context: CallbackContext) -> None:
    user_input = update.message.text
    parts = user_input.split()
    if len(parts) == 3:
        name, phone, email = parts
        # Проверяем, существует ли пользователь с такими данными
        user_data = (name, phone, email)
        # Ищем пользователя по данным
        for user_id, stored_data in users.items():
            if stored_data[1:] == user_data:
                await update.message.reply_text('Вы успешно вошли в систему.')
                return
        await update.message.reply_text('Данные для входа неверны. Пожалуйста, проверьте свои данные и попробуйте еще раз.')
    else:
        await update.message.reply_text('Неверный формат. Пожалуйста, введите имя, номер телефона и email через пробел.')
async def help_command(update: Update, context: CallbackContext) -> None:
    help_text = "Доступные команды:\n"
    help_text += "/start - Запустить бота и показать доступные действия\n"
    help_text += "/info - Получить информацию о ближайших олимпиадах\n"
    help_text += "/register - Зарегистрироваться в боте\n"
    help_text += "/login - Войти в аккаунт\n"
    help_text += "/help - Показать это сообщение справки"
    await update.message.reply_text(help_text)



def main() -> None:
    token = '7311756717:AAFMfLoYeWwxaq6Ip3bTHDwtxU9J7sf0MvY'
    application = Application.builder().token(token).build()

    application.add_handler(CommandHandler('start', start))
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_registration))
    application.add_handler(CommandHandler('login', login))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND),
                                           handle_login))  # Добавляем обработчик текстовых сообщений для входа
    application.add_handler(CommandHandler('help', help_command))
    application.add_error_handler(error_handler)

    job_queue = application.job_queue
    job_queue.run_repeating(send_notifications, interval=86400, first=0)  # Запуск каждые 24 часа

    application.run_polling()


if __name__ == '__main__':
    main()