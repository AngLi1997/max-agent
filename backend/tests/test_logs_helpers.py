import pytest

from app.api.routes.logs import _parse_datetime


def test_parse_datetime_raises_on_invalid_value() -> None:
    with pytest.raises(ValueError, match="时间格式无效"):
        _parse_datetime("not-a-datetime")
