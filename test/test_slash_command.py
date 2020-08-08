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


@sc1.add(command="/sc3", guard=True)
def sc2_accept(params):
    return "guard"


@pytest.mark.parametrize("slack_payload,ideal_result", [
        (generate_slash_command_payload(command="/sc1"), "sc1_accept"),
        (generate_slash_command_payload(command="/sc2"), "sc2_accept"),
        (generate_slash_command_payload(command="/sc1", user_id="B"), "after_sc1_accept_user_B"),
        (generate_slash_command_payload(command="/sc1", user_id="A"), "sc1_accept_user_A"),
        (generate_slash_command_payload(command="/sc1", channel_id="Z"), "sc1_accept_channel_Z"),
        (generate_slash_command_payload(command="/none"), "guard")
    ])
def test_slash_command(slack_payload, ideal_result):
    assert sc1.execute(slack_payload) == ideal_result


@pytest.mark.parametrize("slack_payload, description", [
        ({"user_id": ""}, "error no command"),
        ({"command": []}, "error empty command")
    ])
def test_slash_command_error(slack_payload, description):
    with pytest.raises(SlackApiDecoratorException):
        sc1.execute(slack_payload)


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
