import os
import re
import json
import requests
from tkbot.mybot.mytrellobot import TrelloBot
from tkbot.models import Task, User
from tkbot.extensions import db


class SlackBot:
    def __init__(self):
        self.trello_bot = TrelloBot()
        self.token = os.environ.get("MY_SLACK_TOKEN")

    def get_username(self, user_id):
        query = {"token": self.token, "user": user_id}
        res = requests.get("https://slack.com/api/users.info", params=query)
        user = json.loads(res.text)
        return user["user"]["real_name"]

    def get_desc(self, thread_ts, channel_id):
        endpoint = f"https://slack.com/api/conversations.replies?token={self.token}&channel={channel_id}&ts={thread_ts}"
        response = json.loads(requests.get(endpoint).text)
        messages = response["messages"][0]
        content = messages["text"]
        user_pattern = re.compile("<@(\w*)>")
        users_tagged = re.findall(user_pattern, content)

        for user in users_tagged:
            content = content.replace(user, self.get_username(user))

        requestor = self.get_username(messages["user"])
        desc = f"- *Người yêu cầu* : **{requestor}**\n***\n{content}\n"
        attachments = []
        if "files" in messages:
            for attach in messages["files"]:
                attachments.append(
                    {
                        "name": attach["name"],
                        "url": attach["url_private"],
                        "mimeType": attach["mimetype"],
                    }
                )
        return {
            "desc": desc,
            "ts": messages["ts"],
            "attachments": attachments,
            "requestor": requestor,
        }

    def reply_in_thread(self, channel, thread_ts, text):
        endpoint = "https://slack.com/api/chat.postMessage"
        data = {
            "token": self.token,
            "channel": channel,
            "text": text,
            "thread_ts": thread_ts,
        }
        response = requests.post(endpoint, data=data)
        if response.status_code == 200:
            return True
        return False

    def post_reaction(self, channel, name, ts):
        endpoint = "https://slack.com/api/reactions.add"
        data = {"token": self.token, "channel": channel, "name": name, "timestamp": ts}
        requests.post(endpoint, data=data)

    def get_members_id(self, members):
        idMembers = []
        for member in members:
            slack_id = member.replace("@", "")
            user = User.query.filter(User.slack_id == slack_id).first()
            if user is not None:
                idMembers.append(user.trello_id)
        return idMembers

    def get_status(self, card_id):
        task = Task.query.filter(Task.card_id == card_id).first()
        if task is not None:
            return task.status
        return None

    def track_status(self, sender, channel, thread_ts):
        task = Task.query.filter(Task.thread_ts == thread_ts).first()
        reply = f"<@{sender}> "
        if task is not None:
            status = task.status
            if status == "todo":
                reply += "\n:memo: *[Todo] :* Task này đã được thêm vào danh sách cần làm và sẽ được triển khai trong thời gian sớm nhất!"
            elif status == "doing":
                reply += "\n:construction_worker: *[Doing] :*  Task này đang được thực hiện, bạn sẽ nhận được thông báo khi task này hoàn thành!"
            elif status == "qc":
                reply += "\n:mag: *[QC] :* Task này cơ bản đã được hoàn thành và đang trong quá trình review trước khi được đưa vào hệ thống!"
            else:
                reply += "\n:ok_hand: *[Done] :* Task này đã được làm xong rồi nhé!"
            self.reply_in_thread(channel, thread_ts, reply)
        else:
            reply += "\n:interrobang: *[Not found] :* Không có thông tin về task này!"
            self.reply_in_thread(channel, thread_ts, reply)

    def update_task(self, colummn, value, id_field, id_value):
        if hasattr(Task, id_field):
            task = Task.query.filter(getattr(Task, id_field) == id_value).first()
            setattr(task, colummn, value)
            db.session.commit()

    def notify_done(self, card_id):
        task = Task.query.filter(Task.card_id == card_id).first()
        if task is not None:
            reply = f"<@{task.requestor}>\n:ok_hand: Task này đã được làm xong rồi nhé!"
            self.post_reaction(task.channel, "white_check_mark", task.timestamp)
            self.reply_in_thread(task.channel, task.thread_ts, reply)

    def process_mention(self, data):
        # Extract neccessary data
        channel = data["event"]["channel"]
        if "thread_ts" in data["event"]:
            thread_ts = data["event"]["thread_ts"]
        else:
            thread_ts = data["event"]["ts"]

        sender = data["event"]["user"]
        text = data["event"]["text"]

        # check if user want to checking task's progress
        result = re.findall(r"<@\w.*> (\w.*)", text)
        if len(result) >= 1:
            status = result[0]
            if status.replace(" ", "").lower() == "status":
                return self.track_status(sender, channel, thread_ts)

        # check if user want to create card
        pattern = re.compile("(?:assign (<@\w.*> )+)?name (\w.*)")
        task = re.findall(pattern, text)
        reply = ""
        if len(task) >= 1:
            detail = self.get_desc(thread_ts, channel)
            # Card information
            desc = detail["desc"]
            idMembers = []
            if task[0][0] != "":
                members = re.findall(r"@\w*", task[0][0])
                idMembers = self.get_members_id(members)
                for member in members:
                    reply += f"<{member}> "
            else:
                reply = f"<@{sender}> "

            card = {"name": task[0][1], "desc": desc, "idMembers": idMembers}

            # Call create card api
            try:
                card_id = self.trello_bot.create_card(card, "todo")
                task = Task(
                    card_id,
                    channel,
                    thread_ts,
                    detail["ts"],
                    detail["requestor"],
                    type="minor",
                )
                db.session.add(task)
                db.session.commit()

                # Add reply
                reply += f"\n:ok_hand: Tạo card thành công!\n:card_index: Id Card: {card_id}\n:link: Link: https://trello.com/c/{card_id}"

                for attach in detail["attachments"]:
                    self.trello_bot.create_attach(
                        card_id, attach["url"], attach["name"], attach["mimeType"]
                    )

                # Mark card created
                self.post_reaction(channel, "card_index", detail["ts"])
                # Notify creator
                return self.reply_in_thread(channel, thread_ts, reply)
            except:
                return False

    def add_task(self, form):
        pattern = re.compile("(?:assign (@\w.*)+)?name (\w.*)")
        data = re.findall(pattern, form.get("text"))
        members = []
        if len(data) == 0:
            return False
        if data[0][0] != "":
            members = [i for i in re.findall(r"@\w*", data[0][0])]

        card = {"name": f"{data[0][1]}"}
        card_id = self.trello_bot.create_card(card, "doing")
        print(f"Created card's id: {card_id}")
        print(f"Member(s): {members}")
        return card_id
