"""
Исправление ошибок ручного ввода в данных государственных регистрационных номеров автомобилей РФ.

Функция normalize возвращает переданный ей номер с исправленными ошибками.

Модуль также содержит константы ALLOWED_LETTERS (разрешенные ГОСТом буквы),
ALLOWED_NUMBERS (цифры), ALLOWED_SYMBOLS (объединение разрешенных букв и цифр)
и ALLOWED_FORMATS (разрешенные форматы строки с номером).
"""

import re
import itertools as it

_repl_old = "ABCEHIKMOPTXYЗ"
_repl_new = "АВСЕН1КМОРТХУ3"
_repl_tuples = set(zip(_repl_old, _repl_new))

ALLOWED_LETTERS = "АВЕКМНОРСТУХ"
ALLOWED_NUMBERS = "0123456789"
ALLOWED_SYMBOLS = ALLOWED_LETTERS + ALLOWED_NUMBERS

ALLOWED_LETTERS = set(ALLOWED_LETTERS)
ALLOWED_NUMBERS = set(ALLOWED_NUMBERS)
ALLOWED_SYMBOLS = set(ALLOWED_SYMBOLS)

# Далее определены возможные форматы госномеров для первых 2 типов госномеров
# согласно ГОСТ Р 50577-2018 (https://ru.wikipedia.org/wiki/Регистрационные_знаки_транспортных_средств_в_России)

ALLOWED_FORMATS = {
    "X999XX99",  # Тип 1 — Регистрационные знаки легковых, грузовых автомобилей и автобусов
    "X999XX999",  # Тип 1 — Регистрационные знаки легковых, грузовых автомобилей и автобусов (3 знака в регионе)
    "XX99999",  # Тип 1Б — Регистрационные знаки для легковых такси
    "XX999999",  # Тип 2 — Регистрационные знаки для автомобильных прицепов и полуприцепов
    # Тип 4А — Регистрационные знаки для внедорожных мототранспортных средств,
    # не предназначенных для движения по автомобильным дорогам общего пользования (снегоболотоходы, мотовездеходы)
    # Тип 6 — Регистрационные знаки для автомобильных прицепов и полуприцепов
    "9999XX99",  # Тип 3 — Регистрационные знаки для тракторов, самоходных дорожно-строительных и иных машин
    # Тип 4 — Регистрационные знаки для мотоциклов
    # Тип 5 — Регистрационные знаки легковых, грузовых автомобилей и автобусов
    # Тип 7 — Регистрационные знаки для тракторов, самоходных дорожно-строительных и иных машин и прицепов (полуприцепов) к ним.
    # Тип 8 — Регистрационные знаки для мотоциклов, внедорожных мототранспортных средств.
    "XX99XX99",  # Тип 4Б — Регистрационные знаки для мопедов
}

"""
>>> 'Ю' in ALLOWED_LETTERS
False

>>> 1 in ALLOWED_NUMBERS
False

>>> '1' in ALLOWED_NUMBERS
True

>>> all([x in ALLOWED_SYMBOLS for x in ALLOWED_NUMBERS])
True

>>> 'X999XX99' in ALLOWED_FORMATS
True
"""


def normalize(no, prefer=None) -> str:
    """Берет на вход государственный регистрационный номер транспортного средства
    с ошибками ручного ввода и возвращает исправленный госномер.

    Поднимает ValueError, если в номере, подаваемом на вход, содержатся ошибки, которые
    невозможно исправить.

    Args:
        no (str): строка с номером, которую требуется нормализовать / исправить.
        prefer (list[str]): перечень предпочитаемых форматов в порядке предпочтения.
            Нужно для случаев, когда номера можно истолковать по-разному.
            Например, `["X999XX999", "X999XX999"]` отдаст предпочтение
            трактовке номеров, как автомобильных (тип 1). А входящая строка "о001тр98"
            будет нормализована как "О001ТР98" (формат номера автомобиля),
            а не как "0001ТР98" (формат номера мопеда).

            Если не указано, то берется первый попавшийся из подошедших форматов.

    Returns:
        str: исправленная, приведенная к стандарту строка с номером.

    Raises:
        ValueError: если строку не удается исправить, т.е. она содержит символы,
            которым невозможно привести в соответствие один из стандартных,
            или вся строка имеет неправильный формат.

    Examples:
    >>> normalize ('YY1239O')
    'УУ12390'

    >>> normalize (12340078)
    '1234ОО78'

    >>> normalize ('о123оо9о9')
    'О123ОО909'

    >>> normalize ('000100102')
    'О001ОО102'

    >>> normalize ('   оо12345  ')
    'ОО12345'

    >>> normalize("о001тр98", ["9999XX99", "XX99XX99", "X999XX99"])
    '0001ТР98'

    >>> normalize ('')
    Traceback (most recent call last):
    ...
    ValueError: Недопустимый формат: ""

    >>> normalize ('000000000')
    Traceback (most recent call last):
    ...
    ValueError: Номер не может содержать числовые последовательности, состоящие только из нулей

    >>> normalize ('000100001')
    Traceback (most recent call last):
    ...
    ValueError: Первая цифра трехзначного региона не может быть нулем

    >>> normalize ('ГН99900')
    Traceback (most recent call last):
    ...
    ValueError: Недопустимый символ: "Г"

    >>> normalize ('НН01ВВ67ОО78')
    Traceback (most recent call last):
    ...
    ValueError: Недопустимый формат: "XX*9XX99**99"

    >>> normalize (12345678)
    Traceback (most recent call last):
    ...
    ValueError: Недопустимый формат: "99999999"

    >>> normalize("о001тр98", ["99999999"])
    Traceback (most recent call last):
    ...
    ValueError: Параметр prefer содержит недопустимые форматы: {'99999999'}
    """

    prefer = check_prefer(prefer)
    no = basic_adjustments(no)
    fmt = build_mask(no)
    possible = find_possible_formats(fmt)
    chosen_fmt = choose_format(prefer, possible)
    no = replace_asterisks_to_chosen_format(no, fmt, chosen_fmt)
    final_checks(no, chosen_fmt)

    return no


def check_prefer(prefer):
    if prefer is None:
        prefer = []

    # проверить prefer

    if prefer:
        not_found = set(prefer) - ALLOWED_FORMATS

        if not_found:
            raise ValueError(
                f"Параметр prefer содержит недопустимые форматы: {not_found}"
            )

    return prefer


def basic_adjustments(no):
    no = str(no).replace(" ", "")  # убрать все пробелы

    no = no.upper()  # все в верхний регистр

    for rt in _repl_tuples:  # латиницу в кириллицу
        no = no.replace(rt[0], rt[1])

    return no


def build_mask(no):
    # строим маску формата номера, где "*"" - "0" или "О", "Х" - буква, "9" - цифра
    fmt = ""

    for char in no:
        if char in "0О":
            fmt = f"{fmt}*"
            continue
        if char in ALLOWED_LETTERS:
            fmt = f"{fmt}X"
            continue
        if char in ALLOWED_NUMBERS:
            fmt = f"{fmt}9"
            continue
        raise ValueError(f'Недопустимый символ: "{char}"')

    return fmt


def find_possible_formats(fmt: str):
    """Возвращаем список всех форматов, под которые подошла строка."""

    found_fmts = set()  # найденные форматы

    asterisk_positions = {i for i in range(len(fmt)) if fmt[i] == "*"}

    starting_fmt = fmt.replace("*", "X")
    if starting_fmt in ALLOWED_FORMATS:
        found_fmts.add(starting_fmt)

    for number_of_digits in range(1, len(asterisk_positions) + 1):
        for positions_of_digits in it.combinations(
            asterisk_positions, number_of_digits
        ):
            attempted_fmt = starting_fmt
            for i in positions_of_digits:
                attempted_fmt = repl_char(attempted_fmt, i, "9")
            if attempted_fmt in ALLOWED_FORMATS:
                found_fmts.add(attempted_fmt)

    if not found_fmts:
        raise ValueError(f'Недопустимый формат: "{fmt}"')

    return found_fmts


def choose_format(prefer, possible):
    for chosen_fmt in prefer:
        if chosen_fmt in possible:
            break

    else:
        chosen_fmt = next(iter(possible))

    return chosen_fmt


def replace_asterisks_to_chosen_format(no: str, fmt: str, chosen_fmt: str):
    for i, char in enumerate(fmt):
        if char == "*":
            new_char = "0" if chosen_fmt[i] == "9" else "О"
            no = repl_char(no, i, new_char)

    return no


def final_checks(no, chosen_fmt: str):
    # проверяем наличие комбинаций вида "000"
    if len(re.findall(r"(^|\D)0+(\D|$)", no)):
        raise ValueError(
            "Номер не может содержать числовые последовательности, состоящие только из нулей"
        )

    # проверяем допустимость региона
    if chosen_fmt.endswith("999") and no[-3] == "0":
        raise ValueError("Первая цифра трехзначного региона не может быть нулем")


def repl_char(s: str, i: int, new_char: str):
    return s[:i] + new_char + s[i + 1 :]


if __name__ == "__main__":
    import doctest

    doctest.testmod()
