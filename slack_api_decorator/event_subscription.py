from typing import Optional, Union, List
from .error import SlackApiDecoratorException


class EventSubscription:
    """

    Examples:
        >>> payload_from_slack = {
        ...     'token': '...',
        ...     'team_id': 'Txxxxxxxx',
        ...     'api_app_id': 'Axxxxxxxx',
        ...     'event':
        ...         {
        ...             'type': 'file_public',
        ...             'file_id': 'Fxxxxxxxxxx',
        ...             'user_id': 'Uxxxxxxxx',
        ...             'file': {'id': 'Fxxxxxxxxxx'},
        ...             'event_ts': '1234567890.000000'
        ...         },
        ...     'type': 'event_callback',
        ...     'event_id': 'Evxxxxxxxxxx',
        ...     'event_time': 1234567890,
        ...     'authed_users': ['Uxxxxxxxx']
        ...     }
        >>> es = EventSubscription("sample")
        >>> @EventSubscription.add(command="/some")
        >>> def some_function(params: dict):
        ...     return {
        ...             "response_type": "in_channel",
        ...             "text": f"{str(params)}"
        ...         }
        >>> es.execute(params=payload_from_slack)
    """
    ignore_user_id_list = []

    def __init__(self, app_name: str):
        self.app_name = app_name
        self._executor_list = []

    @staticmethod
    def _get_event_type_from(params: dict) -> str:
        """
        get user_id from the payload
        """
        if 'event' not in params:
            raise SlackApiDecoratorException()
        if 'type' not in params['event']:
            raise SlackApiDecoratorException()
        return params['event']['type']

    @staticmethod
    def _get_user_id_from(params: dict) -> str:
        """
        get user_id from the payload
        """
        if 'event' not in params:
            raise SlackApiDecoratorException()
        if "user_id" in params['event']:
            return params['event']['user_id']
        elif "user" in params['event']:
            return params['event']['user']
        else:
            raise SlackApiDecoratorException()

    @staticmethod
    def _get_channel_id_from(params: dict) -> dict:
        if 'event' not in params:
            raise SlackApiDecoratorException()
        if "item" in params['event']:
            if "channel" in params['event']['item']:
                return params['event']['item']['channel']
        elif "channel" in params['event']:
            return params['event']['channel']
        else:
            raise SlackApiDecoratorException()

    @staticmethod
    def _get_reaction_from(params: dict) -> str:
        if 'event' not in params:
            raise SlackApiDecoratorException()
        if "reaction" in params['event']:
            return params['event']['reaction']
        else:
            raise SlackApiDecoratorException()

    @staticmethod
    def _generate_matched_function(input_x: Union[str, List[str]], function: callable) -> callable:
        if type(input_x) is str:
            return lambda x: function(x) == input_x
        elif type(input_x) is list:
            return lambda x: function(x) in input_x
        else:
            raise SlackApiDecoratorException()

    def add(self,
            event_type: str,
            user_id: Optional[Union[str, List[str]]] = None,
            channel_id: Optional[Union[str, List[str]]] = None,
            reaction: Optional[Union[str, List[str]]] = None,
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
                condition_list.append(self._generate_matched_function(user_id, self._get_user_id_from))
            if channel_id is not None:
                condition_list.append(self._generate_matched_function(channel_id, self._get_channel_id_from))
            if reaction is not None:
                condition_list.append(self._generate_matched_function(reaction, self._get_reaction_from))
            executor_info = {
                "app_name": self.app_name,
                "event_type": event_type,
                "conditions": condition_list,
                "after": after,
                "function": f,
                "guard": guard
            }
            self._executor_list.append(executor_info)
            return f

        return decorator

    @classmethod
    def add_ignore_user_id_list(cls, user_id: str):
        cls.ignore_user_id_list.append(user_id)

    def execute(self, params: dict):
        event_type = self._get_event_type_from(params=params)
        functions = [v for v in self._executor_list if v['event_type'] == event_type]

        if functions:
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
            guard = [v for v in self._executor_list if v['guard']]
            if len(guard) == 1:
                target = guard[0]
            else:
                raise SlackApiDecoratorException()

        target_function = target['function']
        after_function = target['after']
        if after_function is not None:
            return after_function(target_function(params=params))
        return target_function(params=params)
