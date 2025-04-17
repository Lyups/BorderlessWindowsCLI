# **BorderlessWindowsCLI**

 [![Python Version](https://img.shields.io/badge/python-3.8%20%7C%203.9%20%7C%203.10-blue)](https://www.python.org/) [![Issues](https://img.shields.io/github/issues/Lyups/BorderlessWindowsCLI)](https://github.com/Lyups/BorderlessWindowsCLI/issues)

**BorderlessWindowsCLI** — это простое CLI-приложение, которое позволяет избавиться от рамок окна в играх и приложениях, которые не поддерживают безрамочный режим. Приложение также предоставляет инструменты для получения информации о окне (дескриптор, заголовок, разрешение) и изменения его параметров. Работает только на ОС Windows, для Linux будет другая версия

## **Особенности**
- Получение информации об окне: дескриптор, заголовок, текущее разрешение.
- Установка безрамочного режима для любого окна.
- Восстановление стандартного режима окна.
- Поддержка выбора окна по заголовку или дескриптору.

## Установка
```python
pip install -r requirements.txt
```

## Команды
```cmd
python main.py --help
python main.py get-info
python main.py set-resolution --title <TITLE> | --id <ID>
python main.py set-borderless --title <TITLE> | --id <ID>
python main.py revert-borderless --title <TITLE> | --id <ID>
```
