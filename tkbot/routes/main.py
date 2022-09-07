from flask import Blueprint, request
from tkbot.companybot.gitlabbot import GitLabBot
from tkbot.companybot.slackbot import SlackBot
from tkbot.mybot.mygitlabbot import GitLabBot as MyGitLabBot
from tkbot.mybot.myslackbot import SlackBot as MySlackBot

main = Blueprint("main", __name__)


@main.route("/", methods=["GET"])
def home():
    return "App is running!"


@main.route("/bot", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        data = request.json
        GitLabBot(data)
        return "Got it!"

    return "Waiting for webhooks!"


@main.route("/mybot", methods=["GET", "POST"])
def mybot():
    if request.method == "POST":
        data = request.json
        MyGitLabBot(data)
        return "Got it!"

    return "Waiting for webhooks!"


@main.route("/4handyslackbot", methods=["GET", "POST"])
def company_slack_bot():
    if request.method == "POST":
        data = request.json
        print(data)
        if "type" in data and data["type"] == "url_verification":
            return data["challenge"]

        bot = SlackBot()
        bot.process_mention(data)
        return "Got data!"

    return "Listening to slackbot event!"


@main.route("/slackbot", methods=["GET", "POST"])
def slack_bot():
    if request.method == "POST":
        data = request.json
        print(data)
        if "type" in data and data["type"] == "url_verification":
            return data["challenge"]

        bot = MySlackBot()
        bot.process_mention(data)
        return "Got data!"

    return "Listening to slackbot event!"


@main.route("/addtask", methods=["GET", "POST"])
def add_task():
    if request.method == "POST":
        print(request.form)
        bot = MySlackBot()
        id_card = bot.add_task(request.form)
        if id_card:
            return f"Đã tạo trello card id : {id_card}\nLink: https://trello.com/c/{id_card}"
        return "Lỗi cú pháp tạo card!\nVí dụ: /task add @mention name task_name"

    return "Listening to slackbot event!"
