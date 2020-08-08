from slack_api_decorator import SlashCommand
from slack_api_decorator.error import SlackApiDecoratorException
import pytest


def generate_slash_command_payload(
        command: str = "/...",
        team_id: str = "Txxxxxxxx",
        channel_id: str = "Cxxxxxxxx",
        user_id: str = "Uxxxxxxxx"
):
    return {
        'token': ["..."],
        'team_id': [team_id],
        'team_domain': ['...'],
        'channel_id': [channel_id],
        'channel_name': ['...'],
        'user_id': [user_id],
        'user_name': ['...'],
        'command': [command],
        'text': [...],
        'response_url': ['https://hooks.slack.com/commands/Txxxxxxxx/1234567890/...'],
        'trigger_id': ['[0-9]{13}.[0-9]{12}.[0-9a-z]+']}


payload_from_slack_1 = generate_slash_command_payload(command="/sc1")
payload_from_slack_2 = generate_slash_command_payload(command="/sc2")
payload_from_slack_user_A = generate_slash_command_payload(command="/sc1", user_id="A")
payload_from_slack_user_B = generate_slash_command_payload(command="/sc1", user_id="B")
payload_from_slack_channel_Z = generate_slash_command_payload(command="/sc1", channel_id="Z")

sc1 = SlashCommand("test1")


@sc1.add(command="/sc1", condition=lambda x: x['user_id'][0] == "B", after=lambda x: f"after_{x}_user_B")
@sc1.add(command="/sc1")
def sc1_accept(params):
    return "sc1_accept"


@sc1.add(command="/sc1", condition=lambda x: x['user_id'][0] == "A")
def sc1_accept_user_a(params):
    return "sc1_accept_user_A"


@sc1.add(command="/sc1", condition=lambda x: x['channel_id'][0] == "Z")
def sc1_accept_user_a(params):
    return "sc1_accept_channel_Z"


@sc1.add(command="/sc2")
def sc2_accept(params):
    return "sc2_accept"


def test_normal_sc():
    result = sc1.execute(payload_from_slack_1)
    assert result == "sc1_accept"


def test_normal_sc2():
    result = sc1.execute(payload_from_slack_2)
    assert result == "sc2_accept"


def test_normal_sc1_user_a_after():
    result = sc1.execute(payload_from_slack_user_B)
    assert result == "after_sc1_accept_user_B"


def test_normal_sc_user_a():
    result = sc1.execute(payload_from_slack_user_A)
    assert result == "sc1_accept_user_A"


def test_normal_sc_channel_z():
    result = sc1.execute(payload_from_slack_channel_Z)
    assert result == "sc1_accept_channel_Z"


def test_condition_not_callable_error():
    with pytest.raises(SlackApiDecoratorException):
        @sc1.add(command="/sc1_error", condition="some_string")
        def sc1_condition_error(params):
            return "error"


def test_after_not_callable_error():
    with pytest.raises(SlackApiDecoratorException):
        @sc1.add(command="/sc1_error", after="some_string")
        def sc1_condition_error(params):
            return "error"
