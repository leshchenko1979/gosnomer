'''
Исправление ошибок ручного ввода в данных государственных регистрационных номеров автомобилей РФ.

Функция normalize (no) возвращает переданный ей номер no с исправленными ошибками.

Модуль также содержит константы ALLOWED_LETTERS (разрешенные ГОСТом буквы),
ALLOWED_NUMBERS (цифры), ALLOWED_SYMBOLS (объединение разрешенных букв и цифр)
и ALLOWED_FORMATS (разрешенные форматы строки с номером).
'''

import re

_repl_old = 'ABCEHIKMOPTXYЗ'
_repl_new = 'АВСЕН1КМОРТХУ3'
_repl_tuples = set(zip(_repl_old, _repl_new))

ALLOWED_LETTERS = 'АВЕКМНОРСТУХ'
ALLOWED_NUMBERS = '0123456789'
ALLOWED_SYMBOLS = ALLOWED_LETTERS + ALLOWED_NUMBERS

ALLOWED_LETTERS = set(ALLOWED_LETTERS)
ALLOWED_NUMBERS = set(ALLOWED_NUMBERS)
ALLOWED_SYMBOLS = set(ALLOWED_SYMBOLS)

# Далее определены возможные форматы госномеров для первых 2 типов госномеров
# согласно ГОСТ Р 50577-2018 (https://ru.wikipedia.org/wiki/Регистрационные_знаки_транспортных_средств_в_России)

ALLOWED_FORMATS = {
    'Х999ХХ99',  # Тип 1 — Регистрационные знаки легковых, грузовых автомобилей и автобусов 
    'Х999ХХ999', # Тип 1 — Регистрационные знаки легковых, грузовых автомобилей и автобусов (3 знака в регионе)
    'ХХ99999',   # Тип 1Б — Регистрационные знаки для легковых такси
    'ХХ999999',  # Тип 2 — Регистрационные знаки для автомобильных прицепов и полуприцепов
                 # Тип 4А — Регистрационные знаки для внедорожных мототранспортных средств, 
                 # не предназначенных для движения по автомобильным дорогам общего пользования (снегоболотоходы, мотовездеходы)
                 # Тип 6 — Регистрационные знаки для автомобильных прицепов и полуприцепов
    '9999ХХ99',  # Тип 3 — Регистрационные знаки для тракторов, самоходных дорожно-строительных и иных машин
                 # Тип 4 — Регистрационные знаки для мотоциклов
                 # Тип 5 — Регистрационные знаки легковых, грузовых автомобилей и автобусов
                 # Тип 7 — Регистрационные знаки для тракторов, самоходных дорожно-строительных и иных машин и прицепов (полуприцепов) к ним.
                 # Тип 8 — Регистрационные знаки для мотоциклов, внедорожных мототранспортных средств.
    'ХХ99ХХ99'   # Тип 4Б — Регистрационные знаки для мопедов
}

'''
>>> 'Ю' in ALLOWED_LETTERS
False

>>> 1 in ALLOWED_NUMBERS
False

>>> '1' in ALLOWED_NUMBERS
True

>>> all([x in ALLOWED_SYMBOLS for x in ALLOWED_NUMBERS])
True

>>> 'Х999ХХ99' in ALLOWED_FORMATS
True
'''

def normalize(no):
    '''Берет на вход государственный регистрационнй номер авто с ошибками ручного ввода
    и возвращает исправленный госномер.

    Поднимает ValueError, если в номере, подаваемом на вход, содержатся ошибки, которые
    невозможно исправить.

    Args:
        no (str): строка с номером, которую требуется нормализовать / исправить.

    Returns:
        str: исправленная, приведенная к стандарту строка с номером.

    Raises:
        ValueError: если строку не удается исправить, т.е. она содержит символы,
            которым невозможно привести в соответствие один из стандартных,
            или вся строка имеет неправильный формат.

    Examples:
    >>> normalize ('')
    Traceback (most recent call last):
    ...
    ValueError: Недопустимый формат: ""

    >>> normalize ('YY1239O')
    'УУ12390'

    >>> normalize ('000000000')
    Traceback (most recent call last):
    ...
    ValueError: Номер не может содержать числовые последовательности, состоящие только из нулей

    >>> normalize ('000100001')
    Traceback (most recent call last):
    ...
    ValueError: Первая цифра трехзначного региона не может быть нулем

    >>> normalize ('000100102')
    'О001ОО102'

    >>> normalize ('ГН99900')
    Traceback (most recent call last):
    ...
    ValueError: Недопустимый символ: "Г"

    >>> normalize ('   оо12345  ')
    'ОО12345'

    >>> normalize ('НН01ВВ67ОО78')
    Traceback (most recent call last):
    ...
    ValueError: Недопустимый формат: "ХХ*9ХХ99**99"

    >>> normalize (12345678)
    Traceback (most recent call last):
    ...
    ValueError: Недопустимый формат: "99999999"

    >>> normalize (12340078)
    '1234ОО78'

    >>> normalize ('о123оо9о9')
    'О123ОО909'
    '''

    no = str(no).replace(' ', '')  # переводим в строку и убираем все пробелы

    no = no.upper()  # все в верхний регистр

    for rt in _repl_tuples:  # латиницу в кириллицу
        no = no.replace(rt[0], rt[1])

    # строим маску формата номера, где "*"" - "0" или "О", "Х" - буква, "9" - цифра
    f = ''
    for c in no:
        if c in '0О':
            f = f + '*'
            continue
        if c in ALLOWED_LETTERS:
            f = f + 'Х'
            continue
        if c in ALLOWED_NUMBERS:
            f = f + '9'
            continue
        raise ValueError(f'Недопустимый символ: "{c}"')

    # рекурсивно ищем подходящий формат
    def find_acceptable_format(f):
        i = f.find('*')
        if i > -1:
            found_format = find_acceptable_format(f[:i] + 'Х' + f[i+1:])
            if found_format:
                return found_format
            found_format = find_acceptable_format(f[:i] + '9' + f[i+1:])
            if found_format:
                return found_format
        else:
            if f in ALLOWED_FORMATS:
                return f
            else:
                return None

    af = find_acceptable_format(f)

    # подгоняем 0 и О под найденный формат
    if af:
        for i, c in enumerate(f):
            if (c == '*'):
                new_c = '0' if af[i] == '9' else 'О'
                no = no[:i] + new_c + no[i+1:]
    else:
        raise ValueError(f'Недопустимый формат: "{f}"')

    # проверяем наличие комбинаций вида "000"
    if len(re.findall(r'(^|\D)0+(\D|$)', no)) > 0:
        raise ValueError(f'Номер не может содержать числовые последовательности, состоящие только из нулей')

    # проверяем допустимость региона
    if (af == 'Х999ХХ999') and (no[-3:-2] == '0'):
        raise ValueError(f'Первая цифра трехзначного региона не может быть нулем')

    return no


if __name__ == "__main__":
    import doctest
    doctest.testmod()
