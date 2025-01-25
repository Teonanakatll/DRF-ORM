from rich.console import Console
from rich.syntax import Syntax
from pygments.styles import get_style_by_name

from rich.pretty import pprint

# pip install rich
# bold, italic, underline, strikethrough, reverse, blink, reset, color, on_color, link, spoiler, code,
# escaped, bold underline, bold italic, on_, bright_, black, red, green, yellow, blue, magenta, cyan, white, bright_


console = Console()

style = get_style_by_name("fruity")

def cons(*args):
    for i, obj in enumerate(args):
        if len(args) > 1:
            if i == 0:
                console.print(obj, style='#ff00aa bold italic', end=' ')
            elif i == len(args) - 1:
                console.print(obj, style='yellow bold italic')
            else:
                console.print(obj, style='yellow italic', end=' ')
        else:
            console.print(obj, style='#ff00aa bold italic')

            # pprint(obj)
            # syntax = Syntax(str(obj), "sql", theme=style, line_numbers=True)
            # console.print(syntax)


# pip install sqlparse
# from django.db import connection
from django.db.models import QuerySet
from pygments.styles import get_all_styles
import sqlparse

def q(queryset: QuerySet, show_theme=None):
    '''Форматирует и выводит SQL для любого QuerySet.
    :param queryset: QuerySet'''

    if show_theme:
        # Просмотр доступных тем, норм: fruity, github-dark, gruvbox-dark, native, one-dark, zenburn
        sql = str(queryset.query)
        # Форматируем SQL с отступами и большими буквами для ключевых слов
        formatted_sql = sqlparse.format(sql, reindent=True, keyword_case='upper')

        for style in get_all_styles():
            console.rule(f"Theme: {style}")
            syntax = Syntax(formatted_sql, "sql", theme=style, line_numbers=True)
            console.print(syntax)

        return

    try:
        # Преобразуем запрос QuerySet в SQL
        sql = str(queryset.query)
        # Форматируем SQL с отступами и большими буквами для ключевых слов
        formatted_sql = sqlparse.format(sql, reindent=True, keyword_case='upper')

        # Вывод SQL с подсветкой (например, тема "nord-darker, monokai")
        syntax = Syntax(formatted_sql, "sql", theme="native", line_numbers=True)
        cons(syntax)

    except Exception as e:
        console.print(f"[bold red]Ошибка при обработке QuerySet: {e}[/bold red]")


def text(text='\n', filename='gpt4/gpt4.text'):
    """ Функция для сохранения текста в фойл"""
    try:
        with open(filename, 'a', encoding='utf-8') as file:
            if text != '\n':
                file.write(text + '\n')
        cons(f'Текст успешно сохранёт в {filename}')
    except Exception as e:
        cons(f'Ошибка при сохранении текста в файл: {e}')




# Понял, ты хочешь использовать темы в rich и применить их, как это делается в Syntax, а не прописывать стили в каждом вызове функции. Тема в rich позволяет тебе задавать стиль всего вывода или его частей централизованно, а затем просто использовать эти темы для форматирования.
#
# Да, ты можешь использовать темы в rich, чтобы контролировать стиль вывода без необходимости вручную указывать каждый стиль. В твоем случае это будет удобнее, так как можно задать стиль один раз через тему, а потом просто использовать её в функции.
#
# Вот пример, как это можно реализовать:
#
# 1. Создание и использование темы

from rich.console import Console
from rich.theme import Theme
from rich.syntax import Syntax

# Создаем тему с нужными стилями
my_theme = Theme({
    "keyword": "bold red",  # для ключевых слов
    "name": "green",        # для имени
    "string": "italic cyan", # для строк
    "number": "yellow",     # для чисел
    "operator": "bold magenta" # для операторов
})

# # Инициализация консоли с нашей темой
# console = Console(theme=my_theme)
#
# def const(*args):
#     """Выводит несколько аргументов в консоль с заданной темой."""
#     for obj in args:
#         # Можно использовать rich.syntax для форматирования, например, SQL
#         formatted_sql = str(obj)  # Предположим, что это SQL-запрос или строка
#         syntax = Syntax(formatted_sql, "sql", theme=my_theme, line_numbers=True)
#         console.print(syntax)
#
# # Пример вызова
# cons("SELECT * FROM table WHERE id = 1;")