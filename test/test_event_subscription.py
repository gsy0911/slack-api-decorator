from slack_api_decorator import EventSubscription
from slack_api_decorator.error import SlackApiDecoratorException
import pytest


# accept lambda
def accept_reaction_x(reaction) -> callable:
    return lambda x: f"accept_{x}_reaction_{reaction}"


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


payload_from_slack = {
    'token': '...',
    'team_id': 'Txxxxxxxx',
    'api_app_id': 'Axxxxxxxx',
    'event':
        {
            'type': 'file_public',
            'file_id': 'Fxxxxxxxxxx',
            'user_id': 'Uxxxxxxxx',
            'file': {'id': 'Fxxxxxxxxxx'},
            'event_ts': '1234567890.000000'
        },
    'type': 'event_callback',
    'event_id': 'Evxxxxxxxxxx',
    'event_time': 1234567890,
    'authed_users': ['Uxxxxxxxx']
}


event_subscription = EventSubscription("sample")


@event_subscription.add("file_public")
def file_public(params):
    return "file_public_event"


@event_subscription.add("reaction_added", reaction=["sun", "moon"], after=accept_reaction_x("planet"))
@event_subscription.add("reaction_added", reaction="hello", after=accept_reaction_x("morning"))
@event_subscription.add("reaction_added", reaction="+1", after=accept_reaction_x("+1"))
def reaction_added(params):
    return "reaction_added"


def test_file_public():
    result = event_subscription.execute(payload_from_slack)
    assert result == "file_public_event"


@pytest.mark.parametrize("slack_payload, ideal_result", [
    (generate_reaction_payload(reaction="+1"), accept_reaction_x("+1")("reaction_added")),
    (generate_reaction_payload(reaction="hello"), accept_reaction_x("morning")("reaction_added")),
    (generate_reaction_payload(reaction="sun"), accept_reaction_x("planet")("reaction_added")),
    (generate_reaction_payload(reaction="moon"), accept_reaction_x("planet")("reaction_added")),
])
def test_reaction_added(slack_payload, ideal_result):
    assert event_subscription.execute(slack_payload) == ideal_result


@pytest.mark.parametrize("slack_payload, description", [
        ({"user_id": ""}, "error no command"),
        ({"event": []}, "error empty event")
    ])
def test_slash_command_error(slack_payload, description):
    with pytest.raises(SlackApiDecoratorException):
        event_subscription.execute(slack_payload)
