import os
import re
# получаем путь к рабочему столу


desctop_path = os.path.join(os.path.expanduser('~'), 'Desktop')

input_file_path = os.path.join(desctop_path, 'tt2.txt')

main_folder = os.path.join('C:\\Users\\Славик\\Desktop\\django\\books\\gpt4\\dictonary\\')

output_file_path = os.path.join(main_folder, 'test.txt')



# utils = os.path.join('C:\\Users\\Славик\\Desktop\\django\\books\\gpt4\\', 'utils.py')

def text():
    from gpt4.utils import cons
    with open(input_file_path, 'r', encoding='utf-8') as infile:
        data = infile.read()

    temp = re.sub(r'[.,?!]', ' ', data)
    temp = temp.replace('\n', ' ')
    # double = temp.find('up')
    temp = temp.split()
    # temp = map(, temp)
    lst = []

    for i in temp:
        i = i.lower()
        if i not in lst and len(i) > 1 and not i.isdigit():
            lst.append(i)
    lst.sort()
    cons(len(lst))


    with open(output_file_path, 'w', encoding='utf-8') as outfile:
        count = 0
        # num = 0
        for i in lst:
            if count < 16:
                # num += 1
                count += 1
                outfile.write(i + ' ')
            else:
                outfile.write(i + '\n')
                count = 0

source_file = os.path.join(main_folder, 'test.txt')

main_file = os.path.join(main_folder, 'main.txt')

def copy():
    from gpt4.utils import cons
    with open(source_file, 'r', encoding='utf-8') as source:
        source_temp = source.read()
        source_data = source_temp.split()
        cons('source_file:', len(source_data))

    with open(main_file, 'r', encoding='utf-8') as main:
        main_temp = main.read()
        main_data = main_temp.split()
        cons('main_file', len(main_data))

    with open(main_file, 'a', encoding='utf-8') as outfile:
        count = 0
        if len(main_data) == 0:
            main_data = []
        for i in source_data:

            if i not in main_data:
                cons(i)
                if count < 16:
                    count += 1
                    outfile.write(i + ' ')
                else:
                    outfile.write(i + '\n')
                    count = 0

