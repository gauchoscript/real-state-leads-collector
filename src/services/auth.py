import json
import os
import sys
from pathlib import Path

import requests

TOKEN_FILE = Path(__file__).resolve().parent / "auth.json"


class Auth:
    def __init__(self, username=None, password=None):
        self._token = self._load_token() or self.login(username, password)

    def get_token(self):
        return self._token

    def login(self, username=os.getenv("USERNAME"), password=os.getenv("PASSWORD")):
        sys.stdout.write("Logging in...\n")
        payload = {"user": {"username": username, "password": password}}
        response = requests.post(os.getenv("LOGIN_URL"), json=payload)
        token = response.json().get("id_token")

        if token:
            self._save_token(token)

        return token

    def _load_token(self):
        try:
            with open(TOKEN_FILE, "r") as f:
                data = json.load(f)
                return data.get("token")
        except (FileNotFoundError, json.JSONDecodeError):
            return None

    def _save_token(self, token):
        with open(TOKEN_FILE, "w") as f:
            json.dump({"token": token}, f)
