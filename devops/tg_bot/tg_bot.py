import logging
import psycopg2
import re
from dotenv import load_dotenv
import os
import paramiko

from telegram import Update, ForceReply, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler

load_dotenv()
TOKEN = os.getenv('TOKEN')

RM_HOST = os.getenv('RM_HOST')
RM_PORT = os.getenv('RM_PORT')
RM_USER = os.getenv('RM_USER')
RM_PASSWORD = os.getenv('RM_PASSWORD')

FIND_PHONE = 'find_phone_number'

# Подключаем логирование
logging.basicConfig(
    filename='logfile.txt', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

def start(update: Update, context):
    user = update.effective_user
    update.message.reply_text(f'Привет {user.full_name}!')
    

def echo(update: Update, context):
    update.message.reply_text(update.message.text)

def helpCommand(update: Update, context):
    help_message = (
        "Команды:\n"
        "/start - Начать общение с ботом\n"
        "/help - Вывести это сообщение помощи\n"
        "/find_email - Найти email-адреса в тексте\n"
        "/find_phone_number - Найти номера телефонов в тексте\n"
        "/verify_password - проверить сложность пароля\n"
        "/get_release - релиз\n" 
        "/get_uname - архитектура\n"  
        "/get_uptime - время работы\n"  
        "/get_df - файловая система\n"  
        "/get_free - оперативная память\n"  
        "/get_mpstat - производительность\n"
        "/get_w - Сбор информации о работающих в данной системе пользователях\n"  
        "/get_auths - входы\n"  
        "/get_critical - критические события\n"  
        "/get_ps - процессы\n"  
        "/get_ss - порты\n"  
        "/get_apt_list - пакеты\n"  
        "/get_services - сервисы\n"
        "/get_repl_logs - логи репликации\n"
        "/get_emails - вывести email из БД\n"
        "/get_phone_numbers - вывести телефон из БД\n"
    )
    update.message.reply_text(help_message)


def find_phone_number_Command(update: Update, context):
    update.message.reply_text('Введите текст для поиска телефонных номеров: ')

    return 'find_phone_number'

def find_phone_number(update: Update, context):
    user_input = update.message.text
    phoneNumRegex = re.compile(r"(?:(?:8|\+7)[\- ]?)?(?:\(?\d{3}\)?[\- ]?)?[\d\- ]{7,10}")
    phoneNumberList = phoneNumRegex.findall(user_input)

    if not phoneNumberList: # Обрабатываем случай, когда номеров телефонов нет
        update.message.reply_text('Телефонные номера не найдены')
        return ConversationHandler.END
    
    phoneNumbers = ''
    for i in range(len(phoneNumberList)):
        phoneNumbers += f'{i+1}. {phoneNumberList[i]}\n'
    
    update.message.reply_text(phoneNumbers)
    update.message.reply_text('Хотите их записать в базу данных? (да/нет)')

    context.user_data['phoneNumberList'] = phoneNumberList
    return 'confirm_save'

def confirm_save(update: Update, context):
    answer = update.message.text.lower()

    if answer == 'да':
        phoneNumberList = context.user_data.get('phoneNumberList', [])
        save_phones_to_db(phoneNumberList)
        update.message.reply_text('Номера успешно сохранены в базе данных.')
    elif answer == 'нет':
        update.message.reply_text('Операция отменена.')
    else:
        update.message.reply_text('Пожалуйста, ответьте "да" или "нет".')
        return 'confirm_save'
    
    return ConversationHandler.END

# Сохранить номера телефонов в базу данных
def save_phones_to_db(phoneNumberList):
    connection = db_connect()
    if connection is None:
        logging.error('Не удалось подключиться к базе данных.')
        return

    try:
        cursor = connection.cursor()
        for phone in phoneNumberList:
            cursor.execute("INSERT INTO phones (phone_number) VALUES (%s)", (phone,))
        connection.commit()
    except Exception as e:
        logging.error(f"Ошибка при записи номеров в базу данных: {e}")
    finally:
        cursor.close()
        connection.close()

def cancel(update: Update, context):
    update.message.reply_text('Операция отменена.')
    return ConversationHandler.END


def find_email_Command(update: Update, context):
    update.message.reply_text('Введите текст для поиска email: ')

    return 'find_email'

def find_email(update: Update, context):
    user_input = update.message.text
    emailRegex = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
    emailList = emailRegex.findall(user_input)

    if not emailList: # Обрабатываем случай, когда номеров телефонов нет
        update.message.reply_text('Email не найдены')
        return ConversationHandler.END
    
    emails = ''
    for i in range(len(emailList)):
        emails += f'{i+1}. {emailList[i]}\n'
    
    update.message.reply_text(emails)
    update.message.reply_text('Хотите их записать в базу данных? (да/нет)')

    context.user_data['emailList'] = emailList
    return 'confirm_email_save'

def confirm_email_save(update: Update, context):
    answer = update.message.text.lower()

    if answer == 'да':
        emailList = context.user_data.get('emailList', [])
        save_email_to_db(emailList)
        update.message.reply_text('Emails успешно сохранены в базе данных.')
    elif answer == 'нет':
        update.message.reply_text('Операция отменена.')
    else:
        update.message.reply_text('Пожалуйста, ответьте "да" или "нет".')
        return 'confirm_email_save'
    
    return ConversationHandler.END

# Сохранить email в базу данных
def save_email_to_db(emailList):
    connection = db_connect()
    if connection is None:
        logging.error('Не удалось подключиться к базе данных.')
        return

    try:
        cursor = connection.cursor()
        for email in emailList:
            cursor.execute("INSERT INTO emails (email) VALUES (%s)", (email,))
        connection.commit()
    except Exception as e:
        logging.error(f"Ошибка при записи номеров в базу данных: {e}")
    finally:
        cursor.close()
        connection.close()



def verify_password_Command(update: Update, context):
    update.message.reply_text('Введите пароль для его проверки на сложность: ')

    return 'verify_password'

def verify_password(update: Update, context):
    user_input = update.message.text
    passwordRegex = re.compile(
        r'^(?=.*[A-Z])'         
        r'(?=.*[a-z])'
        r'(?=.*\d)'             
        r'(?=.*[!@#$%^&*()])'   
        r'.{8,}$'               
    )
    passwordList = passwordRegex.search(user_input)

    if not passwordList:
        update.message.reply_text('Пароль простой')
    else:
        update.message.reply_text('Пароль сложный')
    
    return ConversationHandler.END






# Мониторинг Linux систем

def ssh_connect(command):

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=RM_HOST, username=RM_USER, password=RM_PASSWORD, port=RM_PORT)
    stdin, stdout, stderr = client.exec_command(command)
    data = stdout.read().decode() + stderr.read().decode()
    client.close()
    return data

# О релизе
def get_release(update: Update, context):
    
    command = "lsb_release -a"
    result = ssh_connect(command)
    update.message.reply_text(result)


# Об архитектуры процессора, имени хоста системы и версии ядра
def get_uname(update: Update, context):
    
    command = "uname -a"
    result = ssh_connect(command)
    update.message.reply_text(result)
    

# О времени работы
def get_uptime(update: Update, context):
    
    command = "uptime -p"
    result = ssh_connect(command)
    update.message.reply_text(result)


# Сбор информации о состоянии файловой системы
def get_df(update: Update, context):
    
    command = "df -h"
    result = ssh_connect(command)
    update.message.reply_text(result)


# Сбор информации о состоянии оперативной памяти
def get_free(update: Update, context):
    
    command = "free -h"
    result = ssh_connect(command)
    update.message.reply_text(result)

# Сбор информации о производительности системы
def get_mpstat(update: Update, context):
    
    command = "mpstat"
    result = ssh_connect(command)
    update.message.reply_text(result)

# Сбор информации о работающих в данной системе пользователях
def get_w(update: Update, context):
    
    command = "w"
    result = ssh_connect(command)
    update.message.reply_text(result)

# Последние 10 входов в систему
def get_auths(update: Update, context):
    
    command = "last -n 10"
    result = ssh_connect(command)
    update.message.reply_text(result)


# Последние 5 критических события
def get_critical(update: Update, context):
    
    command = "journalctl -p 2 -n 5"
    result = ssh_connect(command)
    update.message.reply_text(result)


# Сбор информации о запущенных процессах
def get_ps(update: Update, context):
    
    command = "ps aux | tail"
    result = ssh_connect(command)
    update.message.reply_text(result)


# Сбор информации об используемых портах
def get_ss(update: Update, context):
    
    command = "ss -tuln"
    result = ssh_connect(command)
    update.message.reply_text(result)


# Сбор информации об установленных пакетах

def get_apt_list_Command(update: Update, context):
    update.message.reply_text('Введите название пакета. Если хотите посмотреть все пакеты, то введите "Все пакеты" ')

    return 'get_apt_list'

def get_apt_list(update: Update, context):
    user_input = update.message.text
    if user_input=='Все пакеты':
        command = "dpkg --get-selections | tail"
        result = ssh_connect(command)
        update.message.reply_text(result)
    else:
        command = f"dpkg -l | grep '{user_input}'"
        result = ssh_connect(command)
        if not result:
            update.message.reply_text(f'Пакет "{user_input}" не найден.')
        else:
            update.message.reply_text(result)
    return ConversationHandler.END


# Сбор информации о запущенных сервисах

#def get_services_Command(update: Update, context):
#    update.message.reply_text('Введите название сервиса ')

#    return 'get_services'

def get_services(update: Update, context):
    command = f"service --status-all | grep '\[ + \]' | head -n 15"
    result = ssh_connect(command)
#    if not result:
#        update.message.reply_text(f'Сервис "{user_input}" не найден.')
#    else:
    update.message.reply_text(result)
#    return ConversationHandler.END



# Работа с бд
# Отправка сообщения частями по 4096 символов

def send_message_in_chunks(update, message, chunk_size=4096):
    for i in range(0, len(message), chunk_size):
        update.message.reply_text(message[i:i + chunk_size])


def db_ssh_connect(command):
    DB_HOST = os.getenv('DB_HOST')
    DB_USER = 'postgres'
    DB_PASSWORD = os.getenv('DB_PASSWORD')
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=DB_HOST, username=DB_USER, password=DB_PASSWORD, port=22)
    stdin, stdout, stderr = client.exec_command(command)
    data = stdout.read().decode() + stderr.read().decode()
    client.close()
    return data

# Вывод логов о репликации

def get_repl_logs(update: Update, context):
    log_dir = "/var/log/postgresql/"
    desired_file_pattern = r"postgresql-\d{4}-\d{2}-\d{2}_\d{6}\.log"
    desired_file = None

    try:
        file_list = os.listdir(log_dir)

        for file_name in file_list:
            if re.match(desired_file_pattern, file_name):
                desired_file = os.path.join(log_dir, file_name)

        if desired_file:
            with open(desired_file, 'r') as log_file:
                result = ""
                for line in log_file:
                    if 'replication' in line:
                        result += line

            if len(result) > 4096:
                send_message_in_chunks(update, result)
            else:
                update.message.reply_text(result)
        else:
            update.message.reply_text("No replication logs found.")
    except Exception as e:
        update.message.reply_text(f"Error: {str(e)}")
def db_connect():
    try:
        connection = psycopg2.connect(
            host=os.getenv('DB_HOST'),
            port=os.getenv('DB_PORT'),
            database=os.getenv('DB_DATABASE'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD')
        )
        return connection
    except Exception as e:
        logging.error(f"Ошибка подключения к базе данных: {e}")
        return None

# Получение email 
def get_emails_from_db():
    connection = db_connect()
    if connection is None:
        return "Не удалось подключиться к базе данных."

    try:
        cursor = connection.cursor()
        cursor.execute("SELECT email FROM emails")
        emails = cursor.fetchall()
        return [email[0] for email in emails]
    except Exception as e:
        logging.error(f"Ошибка при получении email-адресов: {e}")
        return "Ошибка при получении email-адресов."
    finally:
        cursor.close()
        connection.close()

# Обработчик команды /get_emails
def get_emails(update: Update, context):
    emails = get_emails_from_db()
    if isinstance(emails, str):
        update.message.reply_text(emails)
    else:
        update.message.reply_text("\n".join(emails) if emails else "Нет email-адресов.")


# Получение номеров 
def get_phone_numbers_from_db():
    connection = db_connect()
    if connection is None:
        return "Не удалось подключиться к базе данных."

    try:
        cursor = connection.cursor()
        cursor.execute("SELECT phone_number FROM phones")
        phone_nubmers = cursor.fetchall()
        return [phone[0] for phone in phone_nubmers]
    except Exception as e:
        logging.error(f"Ошибка при получении номеров телефона: {e}")
        return "Ошибка при получении номеров телефона"
    finally:
        cursor.close()
        connection.close()

# Обработчик команды /get_phone_numbers
def get_phone_numbers(update: Update, context):
    phone_nubmers = get_phone_numbers_from_db()
    if isinstance(phone_nubmers, str):
        update.message.reply_text(phone_nubmers)
    else:
        update.message.reply_text("\n".join(phone_nubmers) if phone_nubmers else "Нет телефонных номеров.")

def main():
		# Создайте программу обновлений и передайте ей токен вашего бота
    updater = Updater(TOKEN, use_context=True)

    # Получаем диспетчер для регистрации обработчиков
    dp = updater.dispatcher
	
    # обработчик
    convHandler_find_phone_number = ConversationHandler(
        entry_points=[CommandHandler('find_phone_number', find_phone_number_Command)],
        states={
            'find_phone_number': [MessageHandler(Filters.text & ~Filters.command, find_phone_number)],
            'confirm_save': [MessageHandler(Filters.text, confirm_save)],
        },
        fallbacks=[]
    )

    convHandler_find_email = ConversationHandler(
        entry_points=[CommandHandler('find_email', find_email_Command)],
        states={
            'find_email': [MessageHandler(Filters.text & ~Filters.command, find_email)],
            'confirm_email_save': [MessageHandler(Filters.text, confirm_email_save)],
        },
        fallbacks=[]
    )

    convHandler_verify_password = ConversationHandler(
        entry_points=[CommandHandler('verify_password', verify_password_Command)],
        states={
            'verify_password': [MessageHandler(Filters.text & ~Filters.command, verify_password)],
        },
        fallbacks=[]
    )

#    convHandler_get_services = ConversationHandler(
#        entry_points=[CommandHandler('get_services', get_services_Command)],
#        states={
#            'get_services': [MessageHandler(Filters.text & ~Filters.command, get_services)],
#        },
#        fallbacks=[]
#    )


    convHandler_get_apt_list = ConversationHandler(
        entry_points=[CommandHandler('get_apt_list', get_apt_list_Command)],
        states={
            'get_apt_list': [MessageHandler(Filters.text & ~Filters.command, get_apt_list)],
        },
        fallbacks=[]
    )

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", helpCommand))
    dp.add_handler(convHandler_find_phone_number)
    dp.add_handler(convHandler_find_email)
    dp.add_handler(convHandler_verify_password)
    dp.add_handler(convHandler_get_apt_list)
 #   dp.add_handler(convHandler_get_services)

    dp.add_handler(CommandHandler("get_release", get_release))
    dp.add_handler(CommandHandler("get_uname", get_uname))
    dp.add_handler(CommandHandler("get_uptime", get_uptime))
    dp.add_handler(CommandHandler("get_df", get_df))
    dp.add_handler(CommandHandler("get_free", get_free))
    dp.add_handler(CommandHandler("get_mpstat", get_mpstat))
    dp.add_handler(CommandHandler("get_w", get_w))
    dp.add_handler(CommandHandler("get_auths", get_auths))
    dp.add_handler(CommandHandler("get_critical", get_critical))
    dp.add_handler(CommandHandler("get_ps", get_ps))
    dp.add_handler(CommandHandler("get_ss", get_ss))
    dp.add_handler(CommandHandler("get_repl_logs", get_repl_logs))
    dp.add_handler(CommandHandler("get_emails", get_emails))
    dp.add_handler(CommandHandler("get_phone_numbers", get_phone_numbers))
    dp.add_handler(CommandHandler("get_services", get_services))
	# Регистрируем обработчики команд
    dp.add_handler(CommandHandler("start", start))
		
	# Регистрируем обработчик текстовых сообщений
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))
		
	# Запускаем бота
    updater.start_polling()

	# Останавливаем бота при нажатии Ctrl+C
    updater.idle()

if __name__ == '__main__':
    main()
