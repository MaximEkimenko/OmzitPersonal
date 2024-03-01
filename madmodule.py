import json
import os
import datetime
import time
from calendar import monthrange
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
import psutil
from openpyxl.styles import Font, Alignment, Border, Side, PatternFill
import smtplib
"""
Модуль с разными вспомогательными функциями
'ver 22.12.2023'
"""


def fresh_file(path=os.getcwd() + '\\', keyword='', ext=''):
    """
    Функция возвращает имя файла модифицированного последним в директории path в имени которого есть,
    ключевое слово keyword
    return: latest_file - - полная директория файла с именем
    """
    max_time = 0  # переменная максимального времени корректировки файла
    latest_file = ''  #
    for root, dirs, files in os.walk(path):
        for file in files:
            if keyword in file and '~' not in file and ext in file:
                current_file = os.path.join(root, file)
                file_change_time = os.path.getmtime(current_file)
                if file_change_time > max_time:
                    max_time = file_change_time
                    latest_file = current_file
    return latest_file


def d_m_y_today():
    """
    Функция возвращает сегодняшний день, месяц, год. День и месяц в формате '01-31', '01-12'

    """
    return (datetime.datetime.now().strftime('%d'), datetime.datetime.now().strftime('%m'),
            datetime.datetime.now().year)


def last_month_day(month, year, weekday=False):
    """
    Возвращает количество дней в месяце.
    Если передан параметр weekday = True,
    то возвращается кортеж = день недели первого дня месяца (номер от 0 до 6), последний день месяца
    """
    if weekday:
        return monthrange(int(year), int(month))
    else:
        return monthrange(int(year), int(month))[1]


def restart_decor(**dkwargs):  # параметры декоратора
    """
    Функция для использования в качестве декоратора для перезапуска декорируемой функции attempts раз через
    time_after_attempt секунд
    """

    def outer(func):  # декорируемая функция
        def inner(*args, **kwargs):  # *args, **kwargs вход параметры функции
            attempts = dkwargs['attempts']
            time_after_attempt = dkwargs['time_after_attempt']
            total_attempts = attempts
            while attempts > 0:
                try:
                    return func(*args, **kwargs)
                except Exception as err:
                    print(f"Ошибка {err} на попытке {total_attempts - (attempts - 1)}. Время попытки: "
                          f"{datetime.datetime.now().time().strftime('%H:%M:%S')}. Попыток осталось {attempts - 1}.")
                    attempts -= 1
                    time.sleep(time_after_attempt)
        return inner
    return outer


def find_file(search_dir, filename):
    """"
    Функция находить файл filename в директории search_dir включая вложенные папки
    возвращает
    """
    for root, dirs, files in os.walk(search_dir):
        for file in files:
            if file in filename:
                return fr'{root}\{file}'


def create_list(dir_path: str, result_type: str, extension: str = '') -> list:
    """
    Функция возвращает список файлов с расширением extension при result_type=files и папок в директории dir_path
    при result_type=dirs не включая вложенные папки
    при result_type=all_files в список добавляются все файлы включая под паки dir_path
    """
    file_list = []
    dirs_list = []
    for root, path_dirs, path_files in os.walk(dir_path):
        if result_type == 'all_files':
            for file in path_files:
                if extension in file and '~' not in file:
                    file_list.append(fr'{root}\{file}')
            return file_list
        if result_type == 'files':
            for file in path_files:
                if extension in file and '~' not in file:
                    if dir_path == root:
                        file_list.append(fr'{root}\{file}')
            return file_list
        if result_type == 'dirs':
            for path_dir in path_dirs:
                if dir_path == root:
                    dirs_list.append(fr'{root}\{path_dir}')
            return dirs_list


def cell_width(sh_obj, letters_list: tuple):
    """"
    Функция форматирует ширину колонок по кортежу ('Литера колонки', 'Ширина колонки')
    """
    for letter, value in letters_list:
        sh_obj.column_dimensions[letter].width = value


def cell_formating(cell_obj, sheet_obj=None, col_num=None, borders=None, border_color='000000', row_height=None,
                   fill_color=None, font_size=None, font_name=None, font_bold=None, font_color='000000',
                   hor_align=None, vert_align=None, wrap_text=None, number_format=None):
    """
    Программа форматирует выбранную ячейку
    cell_obj передается в виде  cell_obj = sheet_obj [f'A{str(i)}'] - ячейка
    sheet_obj объект листа openpyxl
    feel_color = "FF6505"
    col_num - int номера колонки
    return: None
    """
    if borders:
        borders_thin = Side(border_style="thin", color=border_color)  # стиль границы
        cell_obj.border = Border(top=borders_thin, bottom=borders_thin, left=borders_thin, right=borders_thin)
    if row_height and col_num:
        sheet_obj.row_dimensions[col_num].height = row_height
    if fill_color:
        cell_obj.fill = PatternFill('solid', fgColor=fill_color)
    if font_size and font_name:
        cell_obj.font = Font(size=font_size, name=font_name, bold=font_bold, color=font_color)
    if hor_align and vert_align:
        cell_obj.alignment = Alignment(horizontal=hor_align, vertical=vert_align, wrapText=wrap_text)
    if number_format:
        cell_obj.number_format = number_format


def speed_test(function):
    """
    Функция принимает функцию и возвращает кортеж с результатом функции и временем её выполнения
    :param function:
    :return:
    """
    def wrapper(*args, **kwargs):
        start_time = time.time()
        target_function = function(*args, **kwargs)
        result_time = time.time() - start_time
        print(result_time)
        return target_function, result_time
    return wrapper


def process_run_check(json_pid_file_path: str, process_name: str, process_bat_path: str) -> list:
    """
    Функция перезапускает процесс с именем process_name по bat файлу process_bat_path в случае если его PID нет в
    файле обратной связи json_file_name, который создает запускаемый процесс
    :param json_pid_file_path:
    :param process_name: имя процесса
    :param process_bat_path:
    :return: список всех активных процессов на момент запуска process_run_check
    """
    with open(json_pid_file_path, 'r') as file:  # чтение файла обратной связи
        feedback_dict = json.load(file)
    is_running = False
    pid_list = []
    for process in psutil.process_iter():
        pid_list.append((process.pid, process.name()))
        if process.pid == feedback_dict['PID'] and feedback_dict['process_name'] == process_name:
            is_running = True
            break
    if not is_running:
        os.startfile(process_bat_path)
        print(f'Restarting {process_name}...')
    return pid_list


def feedback_json_create(json_pid_file_path: str) -> str:
    """
    Функция создает json файл обратной связи json_file_path c PID, PPID и именем процесса
    :param json_pid_file_path:
    :return: строку с текстом результатом
    """
    PID = os.getpid()  # id процесса
    PARENT_PID = os.getppid()  # id для родительского процесса
    feedback_list = {'datetime': str(datetime.datetime.now()), 'PID': PID, 'PARENT_PID': PARENT_PID,
                     'process_name': psutil.Process(PID).name()}
    try:
        with open(json_pid_file_path, 'w') as jsonfile:
            jsonfile.write(json.dumps(feedback_list))
            result = 'Файл обратной связи создан.\n'
    except Exception as e:
        print(e)
        result = f'При создании файла возникла ошибка: {e}'
    return result


def send_mail_to(file_list: list, receivers_list: list) -> None:
    """
    Функция отправляет пустое письмо реципиентам из receivers_list из списка файлов file_list
    :param file_list:
    :param receivers_list:
    :return: None
    """
    today = datetime.date.today().strftime('%d.%m.%Y')  # сегодня
    now = datetime.datetime.now().strftime('%d.%m.%Y %H:%M')
    for file in file_list:  # проверка наличия файлов
        if not os.path.exists(file):
            print(file)
            raise FileNotFoundError
    for receiver in receivers_list:  # отправка сообщения
        try:
            addr_from = 'omzit-report@yandex.ru'  # данные api почтового сервиса
            password = 'lacwpquciwybdxki'  # данные api почтового сервиса
            msg = MIMEMultipart()  # объект сообщения
            msg['From'] = addr_from  # от
            msg['To'] = receiver  # кому
            msg['Subject'] = f'send{os.path.basename(file_list[0])}-{today}'  # тема
            # прикрепление файлов
            for file in file_list:
                if os.path.isfile(file):
                    filename = os.path.basename(file)  # имя файла
                    ctype = 'application/octet-stream'  # общий тип файла
                    maintype, subtype = ctype.split('/', 1)  # тип и подтип
                    with open(file, 'rb') as fp:
                        file = MIMEBase(maintype, subtype)
                        file.set_payload(fp.read())  # Добавляем содержимое общего типа (полезную нагрузку)
                        encoders.encode_base64(file)  # Содержимое должно кодироваться как Base64
                    file.add_header('Content-Disposition', 'attachment', filename=filename)  # заголовки
                    msg.attach(file)  # Присоединяем файл к сообщению
            # настройка подключения
            server = smtplib.SMTP_SSL('smtp.yandex.ru', 465)
            server.login(addr_from, password)
            server.send_message(msg)
            server.quit()
            print(f'Письмо отправлено: {receiver} {now}.')
        except Exception as e:
            print(f'Ошибка при отправке {receiver} {now} :', e)


if __name__ == '__main__':
    process_bat_path_tst = r'D:\АСУП\Python\Projects\omzit_report_bot\omzit_report_bot.bat'
    json_pid_file_path_tst = r"D:\АСУП\Python\Projects\omzit_report_bot\bd_back_uo_sender_pid.json"
    process_run_check(json_pid_file_path=json_pid_file_path_tst, process_bat_path=process_bat_path_tst,
                      process_name='python.exe')
