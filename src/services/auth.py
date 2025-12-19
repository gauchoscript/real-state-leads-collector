import json
import os

import sys
from pathlib import Path
from typing import Optional

import requests


class Auth:
    TOKEN_FILE = Path(__file__).resolve().parent / "auth.json"
    LOGIN_URL = os.getenv("LOGIN_URL")

    def __init__(self, username: Optional[str] = None, password: Optional[str] = None):
        self._username = username or os.getenv("USERNAME")
        self._password = password or os.getenv("PASSWORD")

        if self._username is None or self._password is None:
            raise ValueError(
                "Username and password must be provided either as arguments or environment variables."
            )

        self._token = self._load_token() or self.login()

    def get_token(self):
        return self._token

    def login(self):
        sys.stdout.write("Logging in...\n")
        payload = {"user": {"username": self._username, "password": self._password}}

        if not Auth.LOGIN_URL:
            raise ValueError("LOGIN_URL environment variable is not set.")

        response = requests.post(Auth.LOGIN_URL, json=payload)
        token = response.json().get("id_token")

        if token:
            self._save_token(token)
            return token
        else:
            sys.exit("Login failed. No token received.\n")

    def _load_token(self):
        try:
            with open(Auth.TOKEN_FILE, "r") as f:
                data = json.load(f)
                return data.get("token")
        except (FileNotFoundError, json.JSONDecodeError):
            return None

    def _save_token(self, token: str):
        with open(Auth.TOKEN_FILE, "w") as f:
            json.dump({"token": token}, f)
