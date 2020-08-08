from typing import Optional, Union, List
from .error import SlackApiDecoratorException


class SlashCommand:
    """

    Examples:
        >>> payload_from_slack = {
        ...     'token': ['...'],
        ...     'team_id': ['Txxxxxxxx'],
        ...     'team_domain': ['...'],
        ...     'channel_id': ['Cxxxxxxxx'],
        ...     'channel_name': ['...'],
        ...     'user_id': ['Uxxxxxxxx'],
        ...     'user_name': ['...'],
        ...     'command': ['/...'],
        ...     'text': [...],
        ...     'response_url': ['https://hooks.slack.com/commands/Txxxxxxxx/1234567890/...'],
        ...     'trigger_id': ['[0-9]{13}.[0-9]{12}.[0-9a-z]+']}
        >>> sc = SlashCommand("sample")
        >>> @sc.add(command="/some")
        >>> def some_function(params: dict):
        ...     return {
        ...             "response_type": "in_channel",
        ...             "text": f"{str(params)}"
        ...         }
        >>> sc.execute(params=payload_from_slack)
    """

    def __init__(self, app_name: str):
        self.app_name = app_name
        self.executor_list: list = []
        self.guard = None

    @staticmethod
    def _get_command_from(params: dict) -> str:
        """
        get command from the payload
        """
        if 'command' not in params:
            raise SlackApiDecoratorException()
        if len(params['command']) == 0:
            raise SlackApiDecoratorException()
        return params['command'][0]

    @staticmethod
    def _generate_matched_function(key: str, input_x: Union[str, List[str]]) -> callable:
        if type(input_x) is str:
            return lambda x: input_x == x[key][0]
        elif type(input_x) is list:
            return lambda x: x[key][0] in input_x
        else:
            raise SlackApiDecoratorException()

    def _add_to_instance(self, executor_info: dict):
        self.executor_list.append(executor_info)

    def add(self,
            command: str,
            user_id: Optional[Union[str, List[str]]] = None,
            channel_id: Optional[Union[str, List[str]]] = None,
            condition: callable = None,
            after: callable = None,
            guard=False):
        def decorator(f):
            if not (callable(condition) or condition is None):
                raise SlackApiDecoratorException()
            if not (callable(after) or after is None):
                raise SlackApiDecoratorException()

            condition_list = []
            if condition is not None:
                condition_list.append(condition)
            if user_id is not None:
                condition_list.append(self._generate_matched_function("user_id", user_id))
            if channel_id is not None:
                condition_list.append(self._generate_matched_function("channel_id", channel_id))
            executor_info = {
                "app_name": self.app_name,
                "command": command,
                "conditions": condition_list,
                "after": after,
                "function": f,
                "guard": guard
            }
            self._add_to_instance(executor_info)
            return f

        return decorator

    def execute(self, params: dict):
        command = self._get_command_from(params=params)
        functions = [v for v in self.executor_list if v['command'] == command]

        if functions:
            if len(functions) == 1:
                # 最初から1つの場合はそれを実行
                target = functions[0]
            else:
                functions_with_condition = [v for v in functions if v['conditions']]
                functions_pass_condition = [v for v in functions_with_condition
                                            if all([f(params) for f in v['conditions']])]
                functions_as_guard = [v for v in functions if not v['conditions']]
                if len(functions_pass_condition) == 1:
                    target = functions_pass_condition[0]
                else:
                    if len(functions_as_guard) == 1:
                        target = functions_as_guard[0]
                    else:
                        raise SlackApiDecoratorException()

        else:
            guard = [v for v in self.executor_list if v['guard']]
            if len(guard) == 1:
                target = guard[0]
            else:
                raise SlackApiDecoratorException()

        target_function = target['function']
        after_function = target['after']
        if after_function is not None:
            return after_function(target_function(params=params))
        return target_function(params=params)
