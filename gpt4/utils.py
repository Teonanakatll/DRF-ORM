from rich.console import Console
console = Console()

def cons(obj, color='yellow', text='italic'):
    return console.print(obj, style=f'{text} {color}')

def conb(first, second):
    console.print(first, style='blue', end=' - ')
    console.print(second, style='yellow')

def text(text='\n', filename='gpt4/gpt4.text'):
    """ Функция для сохранения текста в фойл"""
    try:
        with open(filename, 'a', encoding='utf-8') as file:
            if text != '\n':
                file.write(text +'\n')
        cons(f'Текст успешно сохранёт в {filename}')
    except Exception as e:
        cons(f'Ошибка при сохранении текста в файл: {e}')

