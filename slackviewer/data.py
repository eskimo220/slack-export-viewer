from slackviewer.db import *
from slackviewer.dl import *
import json

from datetime import datetime
import json
import logging
from pprint import pprint
from itertools import groupby
import os


def prepare():
    session = Session()
    try:
        path = "tmp"
        os.makedirs(path, exist_ok=True)

        users = session.query(User).all()
        team = [u.team for u in users]
        
        if len(users) > 0:
            for u in users:
                os.makedirs(os.path.join(path, u.team), exist_ok=True)
                with open(os.path.join(path, u.team, "users.json"), mode='w') as f:
                    f.write(users[0].json)
        else:
            return False

        channel = session.query(Channel).all()

        for row in channel:
            name = {
                "public_channel": "channels.json",
                "private_channel": "groups.json",
                "im": "dms.json",
            }[row.type]

            with open(os.path.join(path, row.team, name), mode='w') as f:
                f.write(row.json)
            for i in json.loads(row.json):
                d = i["name"] if "name" in i else i["id"]
                os.makedirs(os.path.join(path, row.team, d), exist_ok=True)

                for k in session.query(Message).filter(
                        Message.channel == i["id"]).all():
                    with open(os.path.join(path, k.team, d, k.ts + ".json"),
                              mode='w') as ff:
                        ff.write(k.json)
                        print(ff.name)
        session.commit()
        return True
    finally:
        session.close()


def saveData(t):

    dl = slackdl(t)
    session = Session()
    try:
        users = dl.getUsers()
        team_id = users[0]["team_id"]
        session.merge(User(team=team_id, json=json.dumps(users)))

        channel_ids = []
        for c in ["public_channel", "private_channel", "im"]:
            chs = dl.getChannels(c)
            channel_ids += map(lambda k: k["id"], chs)
            session.merge(Channel(team=team_id, type=c, json=json.dumps(chs)))

        for c in channel_ids:
            indb = session.query(Message.ts).filter(
                Message.team == team_id, Message.channel == c).first()
            msg = dl.getMsgs(c, indb[0] if indb is not None else 0)
            if len(msg) > 0:
                session.add(
                    Message(team=team_id,
                            channel=c,
                            ts=msg[0]["ts"],
                            json=json.dumps(msg)))

        session.commit()
    finally:
        session.close()