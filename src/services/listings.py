import json
import requests
import time
import sys
import random
import pytz
import os
from datetime import datetime, timedelta
from src.models import Lead
from src.services.auth import Auth


class Listings:
    MAX_PAGES = 300

    def __init__(self, auth=None):
        self._auth = auth or Auth()
        self._token = self._auth.get_token()
        self._offices = os.getenv("OFFICE_IDS").split(",")
        self._recent_contacted_listings = []

    def _make_api_call(self, params, headers, page, page_size):
        try:
            start = time.time()
            response = requests.get(
                os.getenv("LISTINGS_URL"), params=params, headers=headers, timeout=30
            )
            end = time.time()
            sys.stdout.write(f" Done in {end - start:.2f} seconds.\n")

            # Check HTTP status
            if response.status_code == 401:
                sys.stdout.write(
                    "Unauthorized. Token may have expired. Re-authenticating...\n"
                )
                self._token = self._auth.login()

                if not self._token:
                    sys.exit("Re-authentication failed.\n")

                headers["Authorization"] = f"Bearer {self._token}"
                return self._make_api_call(params, headers, page, page_size)

            if response.status_code != 200:
                sys.stdout.write(
                    f"HTTP Error {response.status_code}: {response.text[:200]}\n"
                )
                return {}

            # Check if response has content
            if not response.content.strip():
                sys.stdout.write("Empty response body\n")
                return {}

            # Check content type
            # Normalize all header keys to lowercase for robust Content-Type detection
            headers_lower = {k.lower(): v for k, v in response.headers.items()}
            content_type = headers_lower.get("content-type", "")
            if "application/json" not in content_type.lower():
                sys.stdout.write(f"Non-JSON response. Content-Type: {content_type}\n")
                sys.stdout.write(f"Response: {response.text[:200]}\n")
                return {}

            # Safe JSON parsing
            try:
                response_data = response.json()
                return response_data
            except json.JSONDecodeError as e:
                sys.stdout.write(f"JSON decode error: {e}\n")
                sys.stdout.write(f"Response content: {response.text[:200]}\n")
                return {}

        except requests.exceptions.Timeout:
            end = time.time()
            sys.stdout.write(f"Request timed out after {end - start:.2f} seconds\n")
            return {}

        except requests.exceptions.ConnectionError as e:
            end = time.time()
            sys.stdout.write(f"Connection error: {e}\n")
            return {}

        except Exception as e:
            end = time.time()
            sys.stdout.write(f"Unexpected error: {e}\n")
            return {}

    def get_listings(self, page=1, page_size=10):
        sys.stdout.write(f"Fetching page {page}...\n")
        sys.stdout.flush()
        params = {
            "type": "sale",
            "associateStatus": "active",
            "combineStatus": "Activas",
            "orderby": "-updated_on",
            "page": page,
            "page_size": page_size,
            "byoffice[]": self._offices,
        }
        headers = {"Authorization": f"Bearer {self._token}"}

        response = self._make_api_call(params, headers, page, page_size)

        if "data" in response:
            for item in response["data"]:
                if item["countContacts"] > 0 and item["status"] == "active":
                    listing_id = item["id"]
                    sys.stdout.write(f"Fetching details for listing {listing_id}...\n")
                    sys.stdout.flush()
                    start = time.time()
                    time.sleep(random.uniform(0.1, 1))
                    # make this api calls persist every 20 pages or so that way they're not completly lost if some error happens
                    self._recent_contacted_listings.append(
                        self._get_listing_details(listing_id)
                    )
                    end = time.time()
                    sys.stdout.write(f" Done in {end - start:.2f} seconds.\n")
                    sys.stdout.flush()

        total_pages = (response or {}).get("searchFilter", {}).get("totalPages", Listings.MAX_PAGES)

        sys.stdout.write(f"Total pages: {total_pages}, \n")
        sys.stdout.flush()
        if page < min(total_pages, Listings.MAX_PAGES):
            time.sleep(random.uniform(0.1, 1))
            return self.get_listings(page + 1, page_size)
        else:
            return self._recent_contacted_listings

    def _get_listing_details(self, listing_id):
        url = f"{os.getenv('LISTING_DETAILS_URL')}/{listing_id}"
        headers = {"Authorization": f"Bearer {self._token}"}

        response = requests.get(url, headers=headers)
        return response.json()

    def get_leads(
        self,
    ):
        recent_contacted_listings = self.get_listings()
        listing_rows = []
        tz = pytz.timezone("America/Argentina/Buenos_Aires")
        now = datetime.now(tz)
        three_days_ago = now - timedelta(days=3)

        for listing in recent_contacted_listings:
            zone = ""
            for key in ["neighborhood", "city", "subregion", "region"]:
                zone = listing["address"].get(key)
                if zone:
                    break

            last_question_hash = None
            for question in listing["question"]["question"]:
                question_date = tz.localize(
                    datetime.strptime(question["received"], "%Y-%m-%d %H:%M:%S")
                )
                question_hash = f"{question['from'].get('email', '')}_{question['from'].get('phone', {}).get('number')}"

                if (
                    three_days_ago <= question_date
                    and question_hash != last_question_hash
                ):
                    listing_rows.append(
                        Lead(
                            listing["mlsid"],
                            question["portal"],
                            question["received"],
                            zone,
                            question["from"]["first_name"],
                            question["from"]["last_name"],
                            question["from"]["email"],
                            question["from"]["phone"]["number"],
                            question["text"].replace("\n", " "),
                        )
                    )
                    last_question_hash = question_hash
        return listing_rows
