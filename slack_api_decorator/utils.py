import urllib.parse
from .error import SlackApiDecoratorException


def decode_text2params(param_text: str, strict=False) -> dict:
    """
    convert ``space-split-text`` to dict.

    Args:
        param_text: space-split-text ex: "--key1 value1 --key2 value2 --key3 value3 ... "
        strict:

    Returns:
        dict

    Examples:
        >>> text = "--key1 value1 --key2 value2 --key3 value3"
        >>> response = decode_text2params(param_text=text)
        >>> response
        ... {
        ...     "--key1": "value1",
        ...     "--key2": "value2",
        ...     "--key3": "value3"
        ... }
    """
    param_text_non_breaking_space_replaced = param_text.replace(u'\xa0', u' ').replace("  ", " ")
    params = param_text_non_breaking_space_replaced.split(" ")
    params_count = len(params)
    if params_count % 2 != 0:
        raise SlackApiDecoratorException(f"parameters must be pair of '--key' and 'value'")

    request_params = {params[i]: urllib.parse.unquote(params[i + 1]) for i in range(0, params_count, 2)}
    if strict:
        if not all([key.startswith("--") for key in list(request_params.keys())]):
            raise SlackApiDecoratorException("parameter key must starts-with '--'")
    return request_params
