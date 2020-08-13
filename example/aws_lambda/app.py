import json
import logging
import urllib.parse

import boto3
from chalice import Chalice
from slack_api_decorator import EventSubscription, SlashCommand

app = Chalice(app_name='aws_example')
event_subscription = EventSubscription(app_name="aws_example")
slash_command = SlashCommand(app_name="aws_example")
logger = logging.getLogger()
logger.setLevel(logging.INFO)
# lambda client to invoke
lambda_client = boto3.client("lambda")


@event_subscription.add("reaction_added")
def receive_reaction_added(params):
    return params


@event_subscription.add(event_type="file_public")
def receive_file_public(params):
    return params


@app.route('/slack/command/handler', methods=['POST'], content_types=['application/x-www-form-urlencoded'])
def receive_command():
    request = app.current_request
    payload = urllib.parse.parse_qs(request.raw_body.decode('utf-8'))
    logger.info(f"payload:= {payload}")

    return slash_command.execute(params=payload)


@app.route('/slack/event/handler', methods=['POST'])
def event_subscription_route():
    request = app.current_request
    payload = request.json_body
    event_handler_lambda = "arn:aws:lambda:ap-{region}-1:{account}:function:{lambda_name}"
    lambda_client.invoke(
        FunctionName=event_handler_lambda,
        InvocationType='Event',
        Payload=json.dumps(payload)
    )

    return payload


@app.lambda_function()
def event_subscription_handler(event, _):
    return event_subscription.execute(params=event)
