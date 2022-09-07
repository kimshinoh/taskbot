import os

SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
SECRET_KEY = os.environ.get("SECRET_KEY")
TRELLO_KEY = os.environ.get("TRELLO_KEY")
TRELLO_TOKEN = os.environ.get("TRELLO_TOKEN")
MY_SLACK_TOKEN = os.environ.get("MY_SLACK_TOKEN")
COMPANY_SLACK_TOKEN = os.environ.get("MY_SLACK_TOKEN")
SQLALCHEMY_TRACK_MODIFICATIONS = False
