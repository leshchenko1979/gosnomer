import pytest

import gosnomer


@pytest.mark.parametrize(
    "in_str, out_str",
    [
        ["YY1239O", "УУ12390"],
        ["000100102", "О001ОО102"],
        ["12340078", "1234ОО78"],
        ["о123оо9о9", "О123ОО909"],
        ["   оо12345  ", "ОО12345"],
    ],
)
def test_success(in_str, out_str):
    assert gosnomer.normalize(in_str) == out_str


@pytest.mark.parametrize(
    "in_str, prefer, out_str",
    [
        ["o123oo97", ["X999XX99"], "О123ОО97"],
        ["o123oo97", ["9999XX99"], "0123ОО97"],
        ["о001тр98", ["X999XX99"], "О001ТР98"],
        ["о001тр98", ["XX99XX99"], "ОО01ТР98"],
        ["о001тр98", ["9999XX99"], "0001ТР98"],
        ["о001тр98", ["9999XX99", "XX99XX99", "X999XX99"], "0001ТР98"],
    ],
)
def test_preferred_formats(in_str, prefer, out_str):
    assert gosnomer.normalize(in_str, prefer) == out_str


@pytest.mark.parametrize(
    "in_str",
    [
        "",
        "YYOOO099",
        "123",
        "000000000",
        "000100001",
        "ГН99900",
        "НН01ВВ67ОО78",
        "12345678",
    ],
)
def test_value_error(in_str):
    with pytest.raises(ValueError):
        gosnomer.normalize(in_str)


def test_wrong_preferred_formats():
    with pytest.raises(ValueError):
        gosnomer.normalize("", [""])


@pytest.mark.parametrize(
    "fmt, possible", [["***9XX99", {"9999XX99", "X999XX99", "XX99XX99"}]]
)
def test_find_possible_formats(fmt, possible: set):
    assert possible.issubset(gosnomer.ALLOWED_FORMATS)
    assert gosnomer.gosnomer.find_possible_formats(fmt) == possible


@pytest.mark.parametrize(
    "s, i, new_char, expected",
    [["a", 0, "b", "b"], ["ab", 0, "c", "cb"], ["ab", 1, "c", "ac"]],
)
def test_repl_char(s, i, new_char, expected):
    assert gosnomer.gosnomer.repl_char(s, i, new_char) == expected
