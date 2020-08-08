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


# instance
sc1 = SlashCommand("test1")

# command list
cmd1 = "/command1"
cmd2 = "/command2"
cmd3 = "/command3"


# accept lambda
def accept_user_x(user) -> callable:
    return lambda x: f"accept_{x}_user_{user}"


# accept lambda
def accept_channel_x(channel) -> callable:
    return lambda x: f"accept_{x}_channel_{channel}"


@sc1.add(command=cmd1, condition=lambda x: x['user_id'][0] == "A", after=accept_user_x("A"))
@sc1.add(command=cmd1, user_id="B", after=accept_user_x("B"))
@sc1.add(command=cmd1, user_id=["C", "D"], after=accept_user_x("CD"))
@sc1.add(command=cmd1, condition=lambda x: x['channel_id'][0] == "Z", after=accept_channel_x("Z"))
@sc1.add(command=cmd1, channel_id="Y", after=accept_channel_x("Y"))
@sc1.add(command=cmd1, channel_id=["W", "X"], after=accept_channel_x("WX"))
@sc1.add(command=cmd1)
def accept_cmd1(params):
    return cmd1


@sc1.add(command=cmd2)
def sc2_accept(params):
    return cmd2


@sc1.add(command=cmd3, guard=True)
def sc2_accept(params):
    return cmd3


@pytest.mark.parametrize("slack_payload,ideal_result", [
        (generate_slash_command_payload(command=cmd1), cmd1),
        (generate_slash_command_payload(command=cmd2), cmd2),
        (generate_slash_command_payload(command=cmd1, user_id="A"), accept_user_x("A")(cmd1)),
        (generate_slash_command_payload(command=cmd1, user_id="B"), accept_user_x("B")(cmd1)),
        (generate_slash_command_payload(command=cmd1, user_id="C"), accept_user_x("CD")(cmd1)),
        (generate_slash_command_payload(command=cmd1, user_id="D"), accept_user_x("CD")(cmd1)),
        (generate_slash_command_payload(command=cmd1, channel_id="Z"), accept_channel_x("Z")(cmd1)),
        (generate_slash_command_payload(command=cmd1, channel_id="Y"), accept_channel_x("Y")(cmd1)),
        (generate_slash_command_payload(command=cmd1, channel_id="W"), accept_channel_x("WX")(cmd1)),
        (generate_slash_command_payload(command=cmd1, channel_id="X"), accept_channel_x("WX")(cmd1)),
        (generate_slash_command_payload(command=cmd3), cmd3),
        (generate_slash_command_payload(command="/none"), cmd3)
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
