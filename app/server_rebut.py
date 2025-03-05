import paramiko


hostname = '90.156.170.66'  # IP или домен сервера
port = 22  # Порт SSH (обычно 22)
username = 'tgbot'  # Имя пользователя на сервере
password = '1972'  # Пароль пользователя
file_app = ('databases.py', 'handlers.py', 'handlers_admin.py', 'func.py', 'keyboards.py', 'handlers_notes.py')
file_main = '../main.py'
server_app = '/home/tgbot/tg_bot/app/'  # Путь на сервере 1
server_main = '/home/tgbot/tg_bot/'
server_app_gal = '/home/tgbot/tg_bot_gal/app/'  # Путь на сервере 2
server_main_gal = '/home/tgbot/tg_bot_gal/'

# Создание SSH клиента
ssh_client = paramiko.SSHClient()
ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    ssh_client.connect(hostname=hostname, port=port, username=username, password=password)
    sftp = ssh_client.open_sftp()
    for file in file_app:
        sftp.put(file, f"{server_app}{file}")
        sftp.put(file, f"{server_app_gal}{file}")
        print(f"Файл {file} успешно загружен на сервер.")

    sftp.put(file_main, f"{server_main}{file_main}")
    sftp.put(file_main, f"{server_main_gal}{file_main}")
    print(f"Файл {file_main} успешно загружен на сервер.")

    sftp.close()


except Exception as e:
    print(f"Ошибка: {e}")

finally:
    # Закрытие соединения
    ssh_client.close()
