from datetime import datetime
from .extensions import db


class User(db.Model):
    __tablename__ = "User"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    slack_id = db.Column(db.String(20), unique=True, index=True)
    trello_id = db.Column(db.String(50), unique=True, index=True)

    def __init__(self, name, slack_id, trello_id):
        self.name = name
        self.slack_id = slack_id
        self.trello_id = trello_id

    def __repr__(self):
        return "<User name={0}; slack_id={1}; trello_id={2}>".format(
            self.name, self.slack_id, self.trello_id
        )


class Task(db.Model):
    __tablename__ = "Task"
    id = db.Column(db.Integer, primary_key=True)
    card_id = db.Column(db.String(10), unique=True, index=True, nullable=False)
    channel = db.Column(db.String(20), nullable=False)
    thread_ts = db.Column(db.String(30), unique=True, index=True)
    timestamp = db.Column(db.String(30), unique=True, index=True)
    requestor = db.Column(db.String(20))
    type = db.Column(db.String(10))
    status = db.Column(db.String(10), default="todo")
    created = db.Column(db.DateTime, nullable=False, default=datetime.now())
    finished = db.Column(db.DateTime, nullable=True, default=None)

    def __init__(
        self,
        card_id,
        channel,
        thread_ts,
        timestamp,
        requestor,
        type,
        status="todo",
        created=datetime.now(),
        finished=None,
    ):
        self.card_id = card_id
        self.channel = channel
        self.thread_ts = thread_ts
        self.timestamp = timestamp
        self.requestor = requestor
        self.type = type
        self.status = status
        self.created = created
        self.finished = finished
