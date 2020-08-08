from slack_api_decorator import EventSubscription
from slack_api_decorator.error import SlackApiDecoratorException
import pytest


# accept lambda
def accept_reaction_x(reaction) -> callable:
    return lambda x: f"accept_{x}_reaction_{reaction}"


# accept lambda
def accept_user_x(user) -> callable:
    return lambda x: f"accept_{x}_user_{user}"


# accept lambda
def accept_channel_x(channel) -> callable:
    return lambda x: f"accept_{x}_channel_{channel}"


def generate_reaction_payload(
        team_id: str = "Txxxxxxxx",
        api_app_id: str = "Axxxxxxxx",
        user_id: str = "Uxxxxxxxx",
        channel_id: str = "Cxxxxxxxx",
        reaction: str = "x"
) -> dict:
    return {
        'token': '...',
        'team_id': team_id,
        'api_app_id': api_app_id,
        'event': {
            'type': 'reaction_added',
            'user': user_id,
            'item': {
                'type': 'message',
                'channel': channel_id,
                'ts': '1234567890.000000'},
            'reaction': reaction,
            'item_user': user_id,
            'event_ts': '1234567890.000000'},
        'type': 'event_callback',
        'event_id': 'Evxxxxxxxxxx',
        'event_time': 1234567890,
        'authed_users': [user_id]}


def generate_file_public_payload(
        team_id: str = "Txxxxxxxx",
        api_app_id: str = "Axxxxxxxx",
        user_id: str = "Uxxxxxxxx"
) -> dict:
    return {
        'token': '...',
        'team_id': team_id,
        'api_app_id': api_app_id,
        'event':
            {
                'type': 'file_public',
                'file_id': 'Fxxxxxxxxxx',
                'user_id': user_id,
                'file': {'id': 'Fxxxxxxxxxx'},
                'event_ts': '1234567890.000000'
            },
        'type': 'event_callback',
        'event_id': 'Evxxxxxxxxxx',
        'event_time': 1234567890,
        'authed_users': [user_id]
    }


def generate_message_payload(
        team_id: str = "Txxxxxxxx",
        api_app_id: str = "Axxxxxxxx",
        user_id: str = "Uxxxxxxxx",
        channel_id: str = "Cxxxxxxxx"):
    return {
        'token': '...',
        'team_id': team_id,
        'api_app_id': api_app_id,
        'event': {
            'client_msg_id': '...',
            'type': 'message',
            'text': 'test',
            'user': user_id,
            'ts': '1234567890.000000',
            'team': team_id,
            'blocks': [
                {
                    'type': 'rich_text',
                    'block_id': 'EBIX',
                    'elements': [{'type': 'rich_text_section', 'elements': [{'type': 'text', 'text': 'test'}]}]
                }],
            'channel': channel_id,
            'event_ts': '1234567890.000000',
            'channel_type': 'channel'},
        'type': 'event_callback',
        'event_id': 'Evxxxxxxxx',
        'event_time': 1234567890,
        'authed_users': [user_id]}


event_subscription = EventSubscription("sample")


# @event_subscription.add("file_public", channel_id="Z", after=accept_channel_x("Z"))
@event_subscription.add("file_public", user_id="A", after=accept_user_x("A"))
@event_subscription.add("file_public")
def file_public(params):
    print(params)
    return "file_public_event"


@event_subscription.add("reaction_added", channel_id="Z", after=accept_channel_x("Z"))
@event_subscription.add("reaction_added", channel_id=["X", "Y"], after=accept_channel_x("XY"))
@event_subscription.add("reaction_added", user_id="A", after=accept_user_x("A"))
@event_subscription.add("reaction_added", user_id=["B", "C"], after=accept_user_x("BC"))
@event_subscription.add("reaction_added", reaction=["sun", "moon"], after=accept_reaction_x("planet"))
@event_subscription.add("reaction_added", reaction="hello", after=accept_reaction_x("morning"))
@event_subscription.add("reaction_added", reaction="+1", after=accept_reaction_x("+1"))
def reaction_added(params):
    print(params)
    return "reaction_added"


@event_subscription.add("reaction_added", reaction="right", channel_id="W",
                        after=lambda x: accept_reaction_x("right")(accept_channel_x("W")(x)))
def mix_reaction_added(params):
    print(params)
    return "mix_reaction_added"


@event_subscription.add("message", channel_id="Z", after=accept_channel_x("Z"))
@event_subscription.add("message", user_id="A", after=accept_user_x("A"))
def message(params):
    print(params)
    return "message"


@event_subscription.add("reaction_added", guard=True)
def guard(params):
    print(params)
    return "guard"


@pytest.mark.parametrize("slack_payload, ideal_result", [
    (generate_file_public_payload(), "file_public_event")
])
def test_file_public(slack_payload, ideal_result):
    assert event_subscription.execute(slack_payload) == ideal_result


@pytest.mark.parametrize("slack_payload, ideal_result", [
    # for reaction
    (generate_reaction_payload(reaction="+1"), accept_reaction_x("+1")("reaction_added")),
    (generate_reaction_payload(reaction="hello"), accept_reaction_x("morning")("reaction_added")),
    (generate_reaction_payload(reaction="sun"), accept_reaction_x("planet")("reaction_added")),
    (generate_reaction_payload(reaction="moon"), accept_reaction_x("planet")("reaction_added")),
    # for user
    (generate_reaction_payload(user_id="A"), accept_user_x("A")("reaction_added")),
    (generate_reaction_payload(user_id="B"), accept_user_x("BC")("reaction_added")),
    (generate_reaction_payload(user_id="C"), accept_user_x("BC")("reaction_added")),
    # for channel
    (generate_reaction_payload(channel_id="Z"), accept_channel_x("Z")("reaction_added")),
    (generate_reaction_payload(channel_id="X"), accept_channel_x("XY")("reaction_added")),
    (generate_reaction_payload(channel_id="Y"), accept_channel_x("XY")("reaction_added")),
    # mix_reaction (reaction + channel)
    (generate_reaction_payload(reaction="right", channel_id="W"),
     accept_reaction_x("right")(accept_channel_x("W")("mix_reaction_added"))),
    # test guard
    (generate_reaction_payload(), "guard"),
])
def test_reaction_added(slack_payload, ideal_result):
    assert event_subscription.execute(slack_payload) == ideal_result


@pytest.mark.parametrize("slack_payload, ideal_result", [
    (generate_message_payload(channel_id="Z"), accept_channel_x("Z")("message")),
    (generate_message_payload(user_id="A"), accept_user_x("A")("message"))
])
def test_message(slack_payload, ideal_result):
    assert event_subscription.execute(slack_payload) == ideal_result


def test_message_error():
    error_subscription = EventSubscription("error")

    @error_subscription.add("message", reaction="+1")
    def event_subscription_message_error(params):
        print(params)

    with pytest.raises(SlackApiDecoratorException):
        error_subscription.execute(generate_message_payload())


def test_file_upload_error_channel_id():
    error_subscription = EventSubscription("error")

    @error_subscription.add("file_upload", channel_id="Z")
    def event_subscription_message_error(params):
        print(params)

    with pytest.raises(SlackApiDecoratorException):
        error_subscription.execute(generate_message_payload())


def test_file_upload_error_reaction():
    error_subscription = EventSubscription("error")

    @error_subscription.add("file_upload", reaction="+1")
    def event_subscription_message_error(params):
        print(params)

    with pytest.raises(SlackApiDecoratorException):
        error_subscription.execute(generate_message_payload())


@pytest.mark.parametrize("slack_payload, description", [
        ({"user_id": ""}, "error no command"),
        ({"event": []}, "error empty event"),
])
def test_event_subscription_error(slack_payload, description):
    with pytest.raises(SlackApiDecoratorException):
        event_subscription.execute(slack_payload)


def test_condition_not_callable_error():
    with pytest.raises(SlackApiDecoratorException):
        @event_subscription.add("reaction_added", condition="some_string")
        def event_subscription_condition_error(params):
            print(params)
            return "error"


def test_after_not_callable_error():
    with pytest.raises(SlackApiDecoratorException):
        @event_subscription.add("reaction_added", after="some_string")
        def event_subscription_condition_error(params):
            print(params)
            return "error"
