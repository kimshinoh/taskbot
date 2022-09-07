from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from models import User

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
User("tknightz", "19292", "22020")
db.session.commit()
User.query.filter(User.name == "tknightz")
