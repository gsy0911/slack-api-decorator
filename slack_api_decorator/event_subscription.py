from inspect import signature
from typing import Optional, Union, List

from .error import SlackParameterNotFoundError, DecoratorAddError, DecoratorExecuteError


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
        >>> @es.add(command="/some")
        >>> def some_function(params: dict):
        ...     return {
        ...             "response_type": "in_channel",
        ...             "text": f"{str(params)}"
        ...         }
        >>> es.execute(params=payload_from_slack)
    """

    def __init__(self, app_name: str):
        self.app_name = app_name
        self._executor_list = []
        self.ignore_user_id_list = []
        
    @staticmethod
    def _get_event(params: dict) -> dict:
        """
        get event dict from slack payload
        
        Args:
            params: payload from slack
        
        Raises:
            if not 'event' in params
        """
        if "event" not in params:
            raise SlackParameterNotFoundError("event", params)
        return params['event']
        
    @staticmethod
    def _get_event_type_from(params: dict) -> str:
        """
        get user_id from the payload
        """
        event = EventSubscription._get_event(params=params)
        if 'type' not in event:
            raise SlackParameterNotFoundError("type", event)
        return event['type']

    @staticmethod
    def _get_user_id_from(params: dict) -> str:
        """
        get user_id from the payload
        """
        event = EventSubscription._get_event(params=params)
        if "user_id" in event:
            return event['user_id']
        elif "user" in event:
            return event['user']
        else:
            raise SlackParameterNotFoundError("user_id", params)

    @staticmethod
    def _get_channel_id_from(params: dict) -> dict:
        event = EventSubscription._get_event(params=params)
        if "item" in event:
            if "channel" in event['item']:
                return event['item']['channel']
        elif "channel" in event:
            return event['channel']
        else:
            raise SlackParameterNotFoundError("channel_id", params)

    @staticmethod
    def _get_reaction_from(params: dict) -> str:
        event = EventSubscription._get_event(params=params)
        if "reaction" in event:
            return event['reaction']
        else:
            raise SlackParameterNotFoundError("reaction", event)

    @staticmethod
    def _generate_matched_function(input_x: Union[str, List[str]], function: callable) -> callable:
        """
        To generate a new function, which receive a dict-argument,
        whether some text(: input_x) contains the dict-argument,
        based on the function(: function) in arguments.
        
        Args:
            input_x:
            function:
            
        Examples:
            >>> user_id = "Uxxxxxxxx"
            >>> new_func = EventSubscription._generate_matched_function(user_id, EventSubscription._get_user_id_from)
            >>> payload_from_slack = {"event": {"user_id": "Uxxxxxxxx"}}
            >>> new_func(payload_from_slack)
            ... True
        
        """
        if type(input_x) is str:
            return lambda x: function(x) == input_x
        elif type(input_x) is list:
            return lambda x: function(x) in input_x
        else:
            raise DecoratorAddError()

    def add(self,
            event_type: str,
            *,
            user_id: Optional[Union[str, List[str]]] = None,
            channel_id: Optional[Union[str, List[str]]] = None,
            reaction: Optional[Union[str, List[str]]] = None,
            condition: callable = None,
            after: callable = None,
            guard=False):
        """
        add function to receive Event Subscription.
        The name of the arguments of registered function must be `params`

        Args:
            event_type: required. the name of the Event Subscription.
            user_id: filter with user_id such as `Uxxxxxxxx`.
            channel_id: filter with channel_id.
            reaction: filter with slack stamp-name.
            condition: additional condition whether the registered function is called.
            after: additional function with recieving the response of the function.
            guard: if True, the registered function is always called.

        Returns:

        """
        def decorator(f):
            sig = signature(f)
            if "params" not in sig.parameters:
                raise DecoratorAddError(f"[params] not in the function [{f.__name__}]")

            if not (callable(condition) or condition is None):
                raise DecoratorAddError("argument [condition] must be callable")
            if not (callable(after) or after is None):
                raise DecoratorAddError("argument [after] must be callable")
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

    def add_ignore_user_id_list(self, user_id: str):
        """
        add ignore user list to avoid being invoked by the app-user
        
        Args:
            user_id: app-user user_id is recommended.
        """
        self.ignore_user_id_list.append(user_id)

    def execute(self, params: dict):
        """

        Args:
            params: payload from Event Subscription of slack.

        Returns:

        """
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
                    raise DecoratorExecuteError("cannot set multiple [guard]")

        else:
            guard = [v for v in self._executor_list if v['guard']]
            if len(guard) == 1:
                target = guard[0]
            else:
                raise DecoratorExecuteError("cannot set multiple [guard]")

        target_function = target['function']
        after_function = target['after']
        if after_function is not None:
            return after_function(target_function(params=params))
        return target_function(params=params)
