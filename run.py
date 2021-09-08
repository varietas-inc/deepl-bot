import os
import logging
from slack_bolt import App
from slack_bolt import Say
from slack_bolt.adapter.socket_mode import SocketModeHandler
import deepl

SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]
SLACK_APP_TOKEN = os.environ["SLACK_APP_TOKEN"]
DEEPL_API_TOKEN = os.environ["DEEPL_API_TOKEN"]

app = App(token=SLACK_BOT_TOKEN)

translator = deepl.Translator(DEEPL_API_TOKEN)

logging.basicConfig(level=logging.DEBUG)


@app.middleware
def log_request(logger, body, next):
    logger.debug(body)
    return next()


@app.event("reaction_added")
def show_datepicker(event, say: Say):
    replies = say.client.conversations_replies(channel=event["item"]["channel"], ts=event["item"]["ts"])
    print(f"replies={replies}")
    message = replies["messages"][0]["text"]
    print(f"message={message}")
    reaction = event["reaction"]
    print(f"reaction={reaction}")

    counts = [x["count"] for x in replies["messages"][0]["reactions"] if x["name"] == reaction]
    print(f"counts={counts}")
    if counts and counts[0] > 1:
        return

    if reaction == "jp":
        target_lang = "JA"
    elif reaction == "us":
        target_lang = "EN-US"
    elif reaction == "gb":
        target_lang = "EN-GB"
    else:
        return
    result = translator.translate_text(message, target_lang=target_lang)
    print(result)
    say(text=f">{message}\n{result.text}", thread_ts=replies["messages"][0].get("thread_ts"))


if __name__ == "__main__":
    handler = SocketModeHandler(app, SLACK_APP_TOKEN)
    handler.start()
