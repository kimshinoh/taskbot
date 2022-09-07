import re
from datetime import datetime
from tkbot.companybot.trellobot import TrelloBot
from tkbot.companybot.slackbot import SlackBot
from tkbot.mybot.mygitlabbot import GitLabBot as MyGitLabBot


class GitLabBot:
    def __init__(self, data):
        self.data = data
        self.trello_bot = TrelloBot()
        self.slack_bot = SlackBot()
        self.process()

    def get_id_card(self):
        id_pattern = re.compile("https://trello.com/c/(\w*)")
        id_card = id_pattern.findall(self.data["object_attributes"]["description"])
        if len(id_card) > 0:
            return id_card[0]
        return None

    def process(self):
        if self.data["object_kind"] == "push":
            print("Got a push event!")
            print(self.data["ref"])
            branch = self.data["ref"].replace("refs/heads/", "")
            extractor_minus = branch.split("-")
            extractor_under = branch.split("_")
            id_card = (
                extractor_minus.pop()
                if len(extractor_minus) > len(extractor_under)
                else extractor_under.pop()
            )
            print(f"Extract id card : {id_card}")
            if self.slack_bot.get_status(id_card) == "todo":
                self.trello_bot.move_card(id_card, "doing")
                self.slack_bot.update_task("status", "doing", "card_id", id_card)

        if self.data["object_kind"] == "merge_request":
            id_card_trello = self.get_id_card()
            print(f"ID card : {id_card_trello}")
            if id_card_trello is None:
                return
            print("Got merge_request")

            if (
                self.data["object_attributes"]["state"] == "opened"
                and self.data["object_attributes"]["work_in_progress"] is False
            ):
                print("Moving card to qc!")
                self.trello_bot.move_card(id_card_trello, "qc")
                self.trello_bot.add_mr(
                    id_card=id_card_trello,
                    mr_link=self.data["object_attributes"]["url"],
                )
                self.slack_bot.update_task("status", "qc", "card_id", id_card_trello)
                print("Moved!")
                return True

            if self.data["object_attributes"]["state"] == "merged":
                print("Moving card to done!")
                self.trello_bot.move_card(id_card_trello, "done")
                self.trello_bot.add_mr(
                    id_card=id_card_trello,
                    mr_link=self.data["object_attributes"]["url"],
                )
                self.slack_bot.update_task("status", "done", "card_id", id_card_trello)
                self.slack_bot.update_task(
                    "finished", datetime.now(), "card_id", id_card_trello
                )
                self.slack_bot.notify_done(id_card_trello)
                print("Notified!")
                print("Moved!")
                return True

            if self.data["object_attributes"]["work_in_progress"] is True:
                print("Moving card to doing!")
                self.trello_bot.move_card(id_card_trello, "doing")
                self.slack_bot.update_task("status", "doing", "card_id", id_card_trello)
                print("Moved!")
                return True
