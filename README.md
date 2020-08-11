# slack-api-decorator

[![PythonVersion](https://img.shields.io/badge/python-3.6|3.7|3.8-blue.svg)](https://www.python.org/downloads/release/python-377/)
[![PiPY](https://img.shields.io/badge/pypi-0.1.0-blue.svg)](https://pypi.org/project/slackapidecorator/)

Slack-API-decorator provides simple decorator to receive slack-payload: `Slash Command` and `Event Subscription`. 

## install

```bash
$ pip install slackapidecorator
```

## usage

### Slash Command

```python
from slack_api_decorator import SlashCommand 
sc = SlashCommand(app_name="sample")

@sc.add(command="/example")
def accept_example(params):
    return params


sc.execute(params={"payload from": "slack"})
```

### Event Subscription

The events below are supported:

* `file_upload`
* `message`
* `reaction_added`

```python
from slack_api_decorator import EventSubscription

event_subscription = EventSubscription(app_name="sample")

@event_subscription.add(event_type="file_upload")
def file_upload_example(params):
    return params

@event_subscription.add("reaction_added", channel_id="Uxxxxxxxx")
def reaction_added_in_channel(params):
    return params

event_subscription.execute(params={"payload from": "slack"})
```