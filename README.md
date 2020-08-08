# slack-api-decorator

## usage

### Slash Command

```python
from slack_api_decorator import SlashCommand 
sc = SlashCommand("sample")

@sc.add(command="/example")
def accept_example(params):
    return params
```
