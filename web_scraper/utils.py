from rich.console import Console

# pip install rich
# bold, italic, underline, strikethrough, reverse, blink, reset, color, on_color, link, spoiler, code,
# escaped, bold underline, bold italic, on_, bright_, black, red, green, yellow, blue, magenta, cyan, white, bright_


console = Console()

# def cons(obj, color='yellow', text='italic'):
#     return console.print(obj, style=f'{text} {color}')

def cons(*args):
    for i, obj in enumerate(args):
        if len(args) > 1:
            if i == 0:
                console.print(obj, style='blue bold italic', end=' ')
            elif i == len(args) - 1:
                console.print(obj, style='yellow bold italic')
            else:
                console.print(obj, style='yellow italic', end=' ')
        else:
            console.print(obj, style='blue bold italic')

def text(text='\n', filename='gpt4/gpt4.text'):
    """ Функция для сохранения текста в фойл"""
    try:
        with open(filename, 'a', encoding='utf-8') as file:
            if text != '\n':
                file.write(text + '\n')
        cons(f'Текст успешно сохранёт в {filename}')
    except Exception as e:
        cons(f'Ошибка при сохранении текста в файл: {e}')

