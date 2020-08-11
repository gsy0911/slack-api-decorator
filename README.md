# slack-api-decorator

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