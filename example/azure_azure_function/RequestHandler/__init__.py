import json
import logging

import azure.functions as func
import requests

logger = logging.getLogger()
logger.setLevel(logging.INFO)

APP_BOT_USER_ID = "Uxxxxxxxx"


def main(req: func.HttpRequest) -> func.HttpResponse:
    payload = req.get_json()
    logger.info(f'payload:{payload}')

    try:
        process_url = ""
        headers = {"Content-Type": "application/json"}
        # すばやくresponseをslack返すことを目的としているため、timeoutを設定している
        _ = requests.post(
            process_url,
            data=json.dumps(payload),
            headers=headers,
            timeout=0.5
        )
    except Exception as e:
        payload['error'] = f"{e.__class__.__name__}: {str(e)}"

    logger.info(payload)
    # 正常終了の場合はSlackへresponseが返る
    return func.HttpResponse(
        body=json.dumps(payload),
        mimetype="application/json",
        charset="utf-8"
    )
