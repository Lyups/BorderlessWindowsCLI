import argparse
import json
import win32gui
import win32con
from ctypes import windll, Structure, c_long, byref
import pygetwindow as gw
import keyboard
import time
import os

CONFIG_DIR = "json_conf"
if not os.path.exists(CONFIG_DIR):
    os.makedirs(CONFIG_DIR)

def calculate_gcd(a, b):
    while b:
        a, b = b, a % b
    return a

def get_cursor_pos():
    class POINT(Structure):
        _fields_ = [("x", c_long), ("y", c_long)]
    pt = POINT()
    windll.user32.GetCursorPos(byref(pt))
    return (pt.x, pt.y)

def get_window(args):
    if args.id:
        hwnd = args.id
        if not win32gui.IsWindow(hwnd):
            print(f"Окно с ID {hwnd} не существует.")
            return None
        try:
            return gw.Win32Window(hwnd)
        except Exception as e:
            print(f"Ошибка при получении окна по ID: {e}")
            return None
    else:
        windows = gw.getWindowsWithTitle(args.title)
        if not windows:
            print(f"Окно с заголовком '{args.title}' не найдено.")
            return None
        return windows[0]

def set_resolution(args):
    window = get_window(args)
    if not window:
        return

    window.resizeTo(args.width, args.height)
    print(f"Разрешение изменено на {args.width}x{args.height}.")

def set_borderless(args):
    window = get_window(args)
    if not window:
        return

    hwnd = window._hWnd
    filename = os.path.join(CONFIG_DIR, f"{hwnd}_styles.json")

    # save json configuration
    original_style = win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE)
    original_exstyle = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
    styles = {
        'original_style': original_style,
        'original_exstyle': original_exstyle
    }
    with open(filename, 'w') as f:
        json.dump(styles, f)

    user32 = windll.user32
    user32.SetWindowLongW(hwnd, win32con.GWL_STYLE, win32con.WS_VISIBLE | win32con.WS_CLIPCHILDREN)
    user32.SetWindowLongW(hwnd, win32con.GWL_EXSTYLE, 0)
    x, y, r, b = win32gui.GetWindowRect(hwnd)
    width = r - x
    height = b - y
    user32.MoveWindow(hwnd, x, y, width, height, True)
    win32gui.SetWindowPos(hwnd, None, x, y, width + 1, height + 1,
                          win32con.SWP_FRAMECHANGED | win32con.SWP_NOZORDER | win32con.SWP_NOOWNERZORDER)
    print("Безрамочный режим активирован.")

def revert_borderless(args):
    window = get_window(args)
    if not window:
        return

    hwnd = window._hWnd
    filename = os.path.join(CONFIG_DIR, f"{hwnd}_styles.json")

    if not os.path.exists(filename):
        print(f"Сохраненные стили для окна с ID {hwnd} не найдены.")
        return

    try:
        with open(filename, 'r') as f:
            styles = json.load(f)
    except FileNotFoundError:
        print(f"Сохраненные стили для окна с ID {hwnd} не найдены.")
        return

    user32 = windll.user32
    user32.SetWindowLongW(hwnd, win32con.GWL_STYLE, styles['original_style'])
    user32.SetWindowLongW(hwnd, win32con.GWL_EXSTYLE, styles['original_exstyle'])

    x, y, r, b = win32gui.GetWindowRect(hwnd)
    width = r - x
    height = b - y
    user32.MoveWindow(hwnd, x, y, width, height, True)
    win32gui.SetWindowPos(hwnd, None, x, y, width + 1, height + 1,
                          win32con.SWP_FRAMECHANGED | win32con.SWP_NOZORDER | win32con.SWP_NOOWNERZORDER)
    print("Безрамочный режим отключён.")

def get_info_interactive():
    print("Наведите курсор на окно и нажмите Ctrl+Alt+A для получения информации.")
    print("Для выхода нажмите Ctrl+Alt+C.")

    hwnd = None
    exit_flag = False

    def on_capture():
        nonlocal hwnd
        x, y = get_cursor_pos()
        hwnd = win32gui.WindowFromPoint((x, y))
        if hwnd == 0:
            print("Окно не найдено. Попробуйте снова.")
        else:
            title = win32gui.GetWindowText(hwnd)
            if not title:
                title = "(без названия)"
            left, top, right, bottom = win32gui.GetWindowRect(hwnd)
            width = right - left
            height = bottom - top
            gcd_value = calculate_gcd(width, height)
            ratio = (width // gcd_value, height // gcd_value)
            print(f"ID окна: {hwnd}, Заголовок: {title}")
            print(f"Текущее разрешение: {width}x{height}")
            print(f"Соотношение сторон: {ratio[0]}:{ratio[1]}")

    def on_exit():
        nonlocal exit_flag
        exit_flag = True

    keyboard.add_hotkey('ctrl+alt+a', on_capture)
    keyboard.add_hotkey('ctrl+alt+c', on_exit)

    try:
        while not exit_flag:
            time.sleep(0.1)
    finally:
        keyboard.unhook_all()

def main():
    parser = argparse.ArgumentParser(description="Управление окнами через CLI")
    subparsers = parser.add_subparsers(dest='command', required=True)

    def add_window_args(parser):
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument('--title', help='Заголовок окна')
        group.add_argument('--id', type=int, help='ID окна (дескриптор)')

    set_parser = subparsers.add_parser('set-resolution', help='Установить разрешение окна')
    add_window_args(set_parser)
    set_parser.add_argument('--width', type=int, required=True, help='Ширина')
    set_parser.add_argument('--height', type=int, required=True, help='Высота')

    borderless_parser = subparsers.add_parser('set-borderless', help='Активировать безрамочный режим')
    add_window_args(borderless_parser)

    revert_parser = subparsers.add_parser('revert-borderless', help='Отключить безрамочный режим')
    add_window_args(revert_parser)

    get_info_parser = subparsers.add_parser('get-info', help='Получить информацию о окне (разрешение, соотношение сторон)')
    group = get_info_parser.add_mutually_exclusive_group(required=False)
    group.add_argument('--title', help='Заголовок окна')
    group.add_argument('--id', type=int, help='ID окна (дескриптор)')

    args = parser.parse_args()

    if args.command == 'set-resolution':
        set_resolution(args)
    elif args.command == 'set-borderless':
        set_borderless(args)
    elif args.command == 'revert-borderless':
        revert_borderless(args)
    elif args.command == 'get-info':
        if args.title or args.id:
            window = get_window(args)
            if window:
                hwnd = window._hWnd
                title = window.title if window.title else "(без названия)"
                width = window.width
                height = window.height
                gcd_value = calculate_gcd(width, height)
                ratio = (width // gcd_value, height // gcd_value)
                print(f"ID окна: {hwnd}, Заголовок: {title}")
                print(f"Текущее разрешение: {width}x{height}")
                print(f"Соотношение сторон: {ratio[0]}:{ratio[1]}")
        else:
            get_info_interactive()

if __name__ == "__main__":
    main()