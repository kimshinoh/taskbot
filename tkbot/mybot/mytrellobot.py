import os
import json
import requests


class TrelloBot:
    def __init__(self):
        self.query = {
            "key": os.environ.get("TRELLO_KEY"),
            "token": os.environ.get("TRELLO_TOKEN"),
        }
        self.map_list = {
            "todo": "5f7addcd0ffbaa4f351c2228",
            "doing": "5f87d86ba339027c8ae0697d",
            "qc": "5f87d86daad8aa44d0c3f8b2",
            "done": "5f884b82afda200910ddd1ff",
        }

        self.map_customFields = {"mr": "5f87da9f9506437a7e9c6149"}

    def create_card(self, card, list_name):
        url = "https://api.trello.com/1/cards"
        query = {**self.query, **card}
        query["idList"] = self.map_list[list_name]
        query["idMembers"] = card["idMembers"]
        response = requests.request("POST", url, params=query)
        if response.status_code == 200:
            short_link = json.loads(response.text)["shortLink"]
            return short_link
        return None

    def create_attach(self, card_id, url, name, mimeType):
        endpoint = f"https://api.trello.com/1/cards/{card_id}/attachments"
        headers = {"Accept": "application/json"}
        query = self.query
        query["url"] = url
        query["name"] = name
        query["mimeType"] = mimeType
        response = requests.request("POST", endpoint, headers=headers, params=query)
        if response.status_code == 200:
            return True
        return False

    def check_mr(self, id_card, mr_link):
        url = f"https://api.trello.com/1/cards/{id_card}/customFieldItems"

        response = requests.request(
            "GET", url, headers={"Accept": "application/json"}, params=self.query
        )

        data = json.loads(response.text)
        for item in data:
            if (
                item["idCustomField"] == self.map_customFields["mr"]
                and item["value"]["text"] == mr_link
            ):
                return True
        return False

    def add_mr(self, id_card, mr_link):
        if self.check_mr(id_card, mr_link):
            print("No need to update mr!")
            return True

        url = f"https://api.trello.com/1/cards/{id_card}/customField/{self.map_customFields['mr']}/item"
        data = {"value": {"text": mr_link}}

        response = requests.request(
            "PUT",
            url,
            headers={"Accept": "application/json"},
            json=data,
            params=self.query,
        )
        if response.status_code == 200:
            print("Updated!")

    def move_card(self, id_card, list_name):
        url = f"https://api.trello.com/1/cards/{id_card}?idList={self.map_list[list_name]}"
        response = requests.request("PUT", url, params=self.query)
        if response.status_code == 200:
            print("Moved Success!")
