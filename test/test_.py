import pytest

import gosnomer


@pytest.mark.parametrize(
    "in_str, out_str",
    [
        ["o123oo97", "О123ОО97"],
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
