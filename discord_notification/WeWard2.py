import json
import requests

class WeWard:
    def __init__(self):
        self.headers = {
            "Host": "backend.prod.weward.fr",
            "user-agent": "okhttp/4.9.1",
            "content-type": "application/json",
            "ww_device_country": "IT",
            "ww_user_language": "it",
        }

    def load_session_no_print(self, session_path):
        data = json.load(open(session_path))
        for k in data:
            setattr(self, k, data[k])

        self.headers.update({"authorization": self.authorization})
        self.challenge_level = 1

        self.user_data = None
        self.get_profile_no_print()

        self.strict_challenges = []
        self.already_visited = []
        self.last_steps = 0

    def get_profile_no_print(self):
        url = "https://backend.prod.weward.fr/api/v1.0/customer/get_profile"
        response = requests.get(url, headers=self.headers)
        self.user_data = response = response.json()
        self.challenge_level = response["challenge_level"]
        return response
