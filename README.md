# gosnomer
 Нормализация для госномеров автомобилей РФ. Автоматическое исправление ошибок ручного ввода госномера.

- Удаление пробелов
- Перевод в верхний регистр
- Перевод латиницы в кириллицу
- Проверка допустимости символов
- Проверка допустимости формата номера
- Исправление ошибок в заменой нуля на букву "О" и наооборот

Примеры использования:

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

Модуль также содержит константы ALLOWED_LETTERS, ALLOWED_NUMBERS, ALLOWED_SYMBOLS и ALLOWED_FORMATS:

    >>> ALLOWED_LETTERS
    'АВЕКМНОРСТУХ'

    >>> ALLOWED_NUMBERS
    '0123456789'

    >>> ALLOWED_SYMBOLS == ALLOWED_LETTERS + ALLOWED_SYMBOLS
    True

    >>> 'Х999ХХ99' in ALLOWED_FORMATS
    True
