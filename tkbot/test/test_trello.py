import unittest
import requests_mock
from tkbot.mybot.myslackbot import SlackBot


class MyTestCase(unittest.TestCase):
    """
    Some test case before push it to Heroku
    """

    def test_get_desc(self):
        bot = SlackBot()
        with open("thread.json", "r") as thread_file:
            mock_response = thread_file.read()

        with open("user.json", "r") as user_file:
            mock_user = user_file.read()

        expected_response = {
            "desc": "- *Người yêu cầu* : **tknightz**\n***\nThis is a test tagged users <@tknightz> <@tknightz> <@tknightz>\n",
            "ts": "1604076408.001700",
            "attachments": [],
        }
        with requests_mock.Mocker() as mocker:
            mocker.register_uri(
                "GET", "https://slack.com/api/conversations.replies", text=mock_response
            )
            mocker.register_uri(
                "GET", "https://slack.com/api/users.info", text=mock_user
            )
            response = bot.get_desc("thread", "channel")
            print(response)
            print(expected_response)
        self.assertEqual(expected_response, response)


if __name__ == "__main__":
    unittest.main()
