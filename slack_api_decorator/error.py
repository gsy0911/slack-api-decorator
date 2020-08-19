class SlackApiDecoratorException(Exception):
    pass


class SlackParameterNotFoundError(SlackApiDecoratorException):
    def __init__(self, missing_key: str, parent_dict: dict):
        self.missing_key = missing_key
        self.parent_dict = parent_dict

    def __str__(self):
        return f"[{self.missing_key}] not found in [{self.parent_dict}]"


class DecoratorAddError(SlackApiDecoratorException):
    pass


class DecoratorExecuteError(SlackApiDecoratorException):
    pass
