import re

_repl_old = 'ABCEHIKMOPTXYЗ'
_repl_new = 'АВСЕН1КМОРТХУ3'
_repl_tuples = list(zip(_repl_old, _repl_new))

_allowed_letters = 'АВЕКМНОРСТУХ'
_allowed_numbers = '0123456789'
_allowed_symbols = _allowed_letters + _allowed_numbers

# Далее определены возможные форматы госномеров для первых 2 типов госномеров
# согласно ГОСТ Р 50577-2018 (https://ru.wikipedia.org/wiki/Регистрационные_знаки_транспортных_средств_в_России)

_allowed_formats = [
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
]


def normalize(no):
    '''Берет на вход государственный регистрационнй номер авто с ошибками ручного ввода
    и возвращает исправленный госномер.

    Поднимает ValueError, если номер не удается исправить.

    Примеры:
    >>> normalize ('')
    Traceback (most recent call last):
    ...
    ValueError: Недопустимый формат: "".

    >>> normalize ('YY1239O')
    'УУ12390'

    >>> normalize ('000000000')
    'О000ОО000'

    >>> normalize ('ГН99900')
    Traceback (most recent call last):
    ...
    ValueError: Недопустимый символ: "Г".

    >>> normalize ('   оо12345  ')
    'ОО12345'

    >>> normalize ('НН01ВВ67ОО78')
    Traceback (most recent call last):
    ...
    ValueError: Недопустимый формат: "ХХ*9ХХ99**99".
    '''

    no = no.replace(' ', '')  # убираем все пробелы

    no = no.upper()  # все в верхний регистр

    for rt in _repl_tuples:  # латиницу в кириллицу
        no = no.replace(rt[0], rt[1])

    # строим маску формата номера, где "*"" - "0" или "О", "Х" - буква, "9" - цифра
    f = ''
    for c in no:
        if c in '0О':
            f = f + '*'
            continue
        if c in _allowed_letters:
            f = f + 'Х'
            continue
        if c in _allowed_numbers:
            f = f + '9'
            continue
        raise ValueError(f'Недопустимый символ: "{c}".')

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
            if f in _allowed_formats:
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
        raise ValueError(f'Недопустимый формат: "{f}".')

    return no


if __name__ == "__main__":
    import doctest
    doctest.testmod()
