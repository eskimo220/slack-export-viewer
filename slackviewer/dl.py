from datetime import datetime
import json
import logging
from pprint import pprint
from itertools import groupby
# logging.basicConfig(level = logging.INFO)
import os
# Import WebClient from Python SDK (github.com/slackapi/python-slack-sdk)
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

# WebClient instantiates a client that can call API methods
# When using Bolt, you can use either `app.client` or the `client` passed to listeners.
client = WebClient(
    token=os.environ.get("SLACK_BOT_TOKEN")
)
logger = logging.getLogger(__name__)


def getUsers(prev=None):
    result = client.users_list(cursor=prev)

    if result["response_metadata"]["next_cursor"]:
        return result["members"] + getUsers(
            result["response_metadata"]["next_cursor"])
    else:
        return result["members"]


def getChannels(type, prev=None):
    result = client.conversations_list(cursor=prev, types=type)

    if result["response_metadata"]["next_cursor"]:
        return result["channels"] + getChannels(
            type, result["response_metadata"]["next_cursor"])
    else:
        return result["channels"]


def getMsgs(channel_id, oldest=0, prev=None):
    result = client.conversations_history(cursor=prev,
                                          oldest=oldest,
                                          channel=channel_id)

    if result["has_more"] and result["response_metadata"]["next_cursor"]:
        return result["messages"] + getMsgs(
            channel_id, oldest, result["response_metadata"]["next_cursor"])
    else:
        return result["messages"]

def writeTofile():

    path = "tmp"
    os.makedirs(path, exist_ok=True)

    with open(os.path.join(path, "users.json"), mode='w') as f:
        json.dump(getUsers(), f, ensure_ascii=False, indent=4)
    with open(os.path.join(path, "channels.json"), mode='w') as f:
        p = getChannels("public_channel") + getChannels("private_channel")
        json.dump(p, f, ensure_ascii=False, indent=4)
        for i in p:
            os.makedirs(os.path.join(path, i["name"]), exist_ok=True)

            for k, g in groupby(
                    reversed(getMsgs(i["id"])), lambda x: datetime.
                    fromtimestamp(float(x["ts"])).strftime('%Y-%m-%d.json')):
                with open(os.path.join(path, i["name"], k), mode='w') as ff:
                    json.dump(list(g), ff, ensure_ascii=False, indent=4)
                    print(ff.name)

    with open(os.path.join(path, "dms.json"), mode='w') as f:
        p = getChannels("im")
        json.dump(p, f, ensure_ascii=False, indent=4)
        for i in p:
            os.makedirs(os.path.join(path, i["id"]), exist_ok=True)

            for k, g in groupby(
                    reversed(getMsgs(i["id"])), lambda x: datetime.
                    fromtimestamp(float(x["ts"])).strftime('%Y-%m-%d.json')):
                with open(os.path.join(path, i["id"], k), mode='w') as ff:
                    json.dump(list(g), ff, ensure_ascii=False, indent=4)
                    print(ff.name)
