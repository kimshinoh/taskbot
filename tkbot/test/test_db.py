from flask import Flask
import unittest

from tkbot.models import User
from tkbot.extensions import db


class appDBTests(unittest.TestCase):
    def test_db(self):
        self.setUp()

    def setUp(self):
        self.app = Flask(__name__)
        self.app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"
        self.app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
        db.init_app(self.app)
        with self.app.app_context():
            db.create_all()
            self.populate_db()
            self.update()
            self.tearDown()

    def populate_db(self):
        user1 = User(name="tknightz", slack_id="slack_id_1", trello_id="trello_id_1")
        db.session.add(user1)
        db.session.commit()

        user2 = User(name="hiep", slack_id="slack_id_2", trello_id="trello_id_2")
        db.session.add(user2)
        db.session.commit()

        try:
            user3 = User(name="hiep", slack_id="slack_id_2", trello_id="trello_id_2")
            db.session.add(user3)
            db.session.commit()
            user_out = db.session.query(User).filter(User.name == "hiep").first()
            self.assertEqual(getattr(user_out, "slack_id"), "slack_id_2")
        except:
            print("Running here!")

    def update(self):
        id_field = "slack_id_3"
        id_value = "slack_id_2"
        if hasattr(User, id_field):
            user_out = User.query.filter(getattr(User, id_field) == id_value).first()
            setattr(user_out, "name", "tulen")
            db.session.commit()

            user_out_1 = User.query.filter(getattr(User, id_field) == id_value).first()
            print(f"Found - {user_out_1}")
            if user_out_1 is not None:
                self.assertEqual(getattr(user_out_1, "name"), "tulen")

    def tearDown(self):
        self.app = Flask(__name__)
        self.app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"
        self.app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
        db.init_app(self.app)
        with self.app.app_context():
            db.drop_all()


if __name__ == "__main__":
    unittest.main()
