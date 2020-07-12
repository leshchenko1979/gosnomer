# gosnomer
 Нормализация для госномеров автомобилей РФ. Автоматическое исправление ошибок ручного ввода госномера.

- Удаление пробелов
- Перевод в верхний регистр
- Перевод латиницы в кириллицу
- Проверка допустимости символов
- Проверка допустимости формата номера
- Исправление ошибок в заменой нуля на букву "О" и наооборот
- Проверка правильности трехзначного кода региона
- Проверка, что числовые последовательности не состоят только из нулей

Примеры использования:
```
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
```

Модуль также содержит наборы ALLOWED_LETTERS, ALLOWED_NUMBERS, ALLOWED_SYMBOLS и ALLOWED_FORMATS:
```
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
```