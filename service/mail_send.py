import smtplib

from email.mime.multipart import MIMEMultipart  # Многокомпонентный объект


def send_email(addr_to, msg_subj):
    """
    Функция отправки письма только с темой
    """
    addr_from = 'omzit-report@yandex.ru'
    password = 'lacwpquciwybdxki'

    msg = MIMEMultipart()  # объект
    msg['From'] = addr_from  # от
    msg['To'] = addr_to  # кому
    msg['Subject'] = msg_subj  # тема
    # настройка подключения
    server = smtplib.SMTP_SSL('smtp.yandex.ru', 465)
    # подключение
    server.login(addr_from, password)
    server.send_message(msg)
    server.quit()
