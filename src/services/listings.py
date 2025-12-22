import os
import random
import sys
import time
from datetime import datetime, timedelta
from typing import Any

import pytz
import requests
from requests import Response

from src.models import Lead
from src.services.auth import Auth


class Listings:
    MAX_PAGES = 300

    def __init__(self, auth: Auth):
        self._auth = auth
        self._token: str = self._auth.get_token()
        self._listings_url = os.getenv("LISTINGS_URL")

        offices = os.getenv("OFFICE_IDS")
        if offices:
            self._offices = offices.split(",")
        else:
            self._offices = None

    def _get_total_pages(self, response: Response) -> int:
        try:
            return response.json().get("searchFilter").get("totalPages")
        except Exception:
            return Listings.MAX_PAGES

    def get_listings(self, page: int = 1, page_size: int = 10):
        accumulated_listings: list[Any] = []

        try:
            while True:
                response = self._get_page(page, page_size)

                for listing_id in self._get_valid_listings(response):
                    sys.stdout.write(f"Fetching details for listing {listing_id}...\n")
                    sys.stdout.flush()
                    start = time.time()
                    time.sleep(random.uniform(0.1, 1))
                    # make this api calls persist every 20 pages or so that way they're not completly lost if some error happens
                    accumulated_listings.append(self._get_listing_details(listing_id))
                    end = time.time()
                    sys.stdout.write(f" Done in {end - start:.2f} seconds.\n")
                    sys.stdout.flush()

                total_pages = self._get_total_pages(response)

                sys.stdout.write(f"Total pages: {total_pages}, \n")
                sys.stdout.flush()

                if page >= min(total_pages, Listings.MAX_PAGES):
                    break
                page += 1

        except Exception as e:
            sys.stdout.write(f"Error occurred while fetching listings: {e}\n")
            sys.stdout.flush()

        return accumulated_listings

    def _check_integrity(self, response: Response):
        if not response.content.strip():
            sys.stdout.write("Empty response body\n")
            return False

        headers_lower = {k.lower(): v for k, v in response.headers.items()}
        content_type = headers_lower.get("content-type", "")
        if "application/json" not in content_type.lower():
            sys.stdout.write(f"Non-JSON response. Content-Type: {content_type}\n")
            sys.stdout.write(f"Response: {response.text[:200]}\n")
            return False

        return True

    def _get_page(self, page: int, page_size: int) -> Response:
        sys.stdout.write(f"Sending request for page: {page}...\n")
        sys.stdout.flush()

        params: dict[str, Any] = {
            "associateStatus": "active",
            "combineStatus": "Activas",
            "orderby": "-updated_on",
            "page": page,
            "page_size": page_size,
        }

        if self._offices:
            params["byoffice[]"] = self._offices

        headers = {"Authorization": f"Bearer {self._token}"}

        try:
            if not self._listings_url:
                raise ValueError("LISTINGS_URL environment variable is not set.")

            start = time.time()

            response = requests.get(
                self._listings_url, params=params, headers=headers, timeout=30
            )

            end = time.time()
            sys.stdout.write(f" Done in {end - start:.2f} seconds.\n")

            response.raise_for_status()

            if not self._check_integrity(response):
                return Response()

            return response

        except requests.exceptions.HTTPError as http_err:
            if http_err.response.status_code == 401:
                sys.stdout.write(
                    "Unauthorized. Token may have expired. Re-authenticating...\n"
                )
                self._token = self._auth.login()

                if not self._token:
                    sys.exit("Re-authentication failed.\n")

                return self._get_page(page, page_size)

            sys.stdout.write(
                f"HTTP Error {http_err.response.status_code}: {http_err.response.text[:200]}\n"
            )
            return Response()

        except Exception as e:
            end = time.time()
            sys.stdout.write(f"Unexpected error: {e}\n")
            return Response()

    def _get_valid_listings(self, response: Response):
        valid_listings: list[str] = []

        try:
            response_data = response.json()

            if "data" in response_data:
                for item in response_data["data"]:
                    if item["countContacts"] > 0 and item["status"] == "active":
                        valid_listings.append(item["id"])

        except Exception as e:
            sys.stdout.write(f"Error parsing listings: {e}\n")

        return valid_listings

    def _get_listing_details(self, listing_id: str):
        url = f"{os.getenv('LISTING_DETAILS_URL')}/{listing_id}"
        headers = {"Authorization": f"Bearer {self._token}"}

        response = requests.get(url, headers=headers)
        return response.json()

    def get_leads(
        self,
    ):
        recent_contacted_listings = self.get_listings()
        listing_rows: list[Lead] = []
        tz = pytz.timezone("America/Argentina/Buenos_Aires")
        now = datetime.now(tz)
        three_days_ago = now - timedelta(days=3)

        for listing in recent_contacted_listings:
            operation_type = "Venta" if listing["type"] == "sale" else "Alquiler"
            
            zone = ""
            for key in ["neighborhood", "city", "subregion", "region"]:
                zone = listing["address"].get(key)
                if zone:
                    break

            last_question_hash = ""
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
                            operation_type,
                            listing["price"]["value"],
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
