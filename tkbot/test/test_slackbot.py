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

        expected_response = {
            "desc": "\u0110\u00e2y l\u00e0 thread \u0111\u1ec3 test ch\u1ee9c n\u0103ng\n-----\n![Screenshot_20200908_174436.png](https://files.slack.com/files-pri/T01C78EK2BZ-F01CZ9FSZ63/screenshot_20200908_174436.png)\n",
            "ts": "1603800958.002000",
        }
        with requests_mock.Mocker() as mocker:
            mocker.register_uri(
                "GET", "https://slack.com/api/conversations.replies", text=mock_response
            )
            response = bot.get_desc("thread", "channel")
        self.assertEqual(expected_response, response)


if __name__ == "__main__":
    unittest.main()
