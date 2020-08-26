from slack_api_decorator import decode_text2params
from slack_api_decorator.error import SlackApiDecoratorException
import pytest


@pytest.mark.parametrize("slack_text, ideal_result", [
    ("--key1 value1", {"--key1": "value1"}),
    ("--key1  value1", {"--key1": "value1"}),
])
def test_decode_text2params(slack_text, ideal_result):
    result = decode_text2params(slack_text)
    assert result == ideal_result


def test_decode_text2params_error():
    with pytest.raises(SlackApiDecoratorException):
        decode_text2params("--key1 value1 --key2")
    with pytest.raises(SlackApiDecoratorException):
        decode_text2params("key1 value1", strict=True)
