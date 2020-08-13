import json
import logging

import azure.functions as func
import requests

from slack_api_decorator import EventSubscription

logger = logging.getLogger()
logger.setLevel(logging.INFO)

APP_BOT_USER_ID = "Uxxxxxxxx"
event_subscription = EventSubscription(app_name="azure_example")


@event_subscription.add("reaction_added")
def receive_reaction_added(params):
    return params


@event_subscription.add(event_type="file_public")
def receive_file_public(params):
    return params


def main(req: func.HttpRequest) -> func.HttpResponse:
    payload = req.get_json()
    logger.info(f'payload:{payload}')

    try:
        event_subscription.execute(params=payload)
    except Exception as e:
        payload['error'] = f"{e.__class__.__name__}: {str(e)}"

    logger.info(payload)
    # 正常終了の場合はSlackへresponseが返る
    return func.HttpResponse(
        body=json.dumps(payload),
        mimetype="application/json",
        charset="utf-8"
    )
