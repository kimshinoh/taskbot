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
            "alltasks": "5958d047795a5f564d0a6b00",
            "specifications": "5f892573e4cf265165085766",
            "todo": "5e5e1391e3c0053b8a4ecadd",
            "doing": "5958d058ce48d6ee6e437912",
            "qc": "5958d05c1f34b876e4fc00a9",
            "done": "5958d06a118336d803b09183",
            "blocked": "5958d06d1717a404723f15e3",
        }

        self.map_customFields = {"mr": "5d25a8c87183ac5dd3475892"}

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
