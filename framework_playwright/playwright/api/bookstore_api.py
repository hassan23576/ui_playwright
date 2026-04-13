import json
import logging
import os
import uuid
from logging import raiseExceptions
from pathlib import Path

import requests
from dotenv import load_dotenv


# Project Root at the top using Pathlib
PROJECT_ROOT = Path(__file__).resolve().parents[3]

load_dotenv(PROJECT_ROOT / ".env")

with open(PROJECT_ROOT / "data" / "config.json") as f:
    config = json.load(f)

BASE_URL = config["base_url"]
ENDPOINTS = config["endpoints"]

logger = logging.getLogger(__name__)


class BookStoreApi:

    def __init__(self):
        self.base_url = BASE_URL
        self.endpoints = ENDPOINTS
        self.project_root = PROJECT_ROOT


    def create_dynamic_user(self):
        """Generate a unique user using API and return user credentials"""
        username = f"user_{uuid.uuid4().hex[:8]}"
        #Fetch password from the environment variable
        password = os.getenv("DEMOQA_PASSWORD")

        if not password:
            raise Exception("DEMOQA_PASSWORD not found in environment variables!")

        # Use endpoint
        url = f"{self.base_url}{ENDPOINTS['create_user']}"
        payload = {"userName": username, "password": password}

        logger.info(f"Attempting to create dynamic user: {username}")

        response = requests.post(url, json=payload)

        if response.status_code == 201:
            api_data = response.json()

            #--- DATA VALIDATION ---
            actual_name = api_data.get("username")
            user_id = api_data.get("userID")

            # Verify the username matches what we sent
            if actual_name != username:
                logger.error(f"DATA MISMATCH: Sent '{username}' but API returned '{actual_name}' ")
                raise ValueError("Username mismatch in API response.")

            # Verify a UserID was generated
            if not user_id:
                logger.error(f"API Error: Response was: {response.status_code} and 'UserID' is missing.")
                raise ValueError("No userID returned from API response.")


            logger.info(f"Successfully created user: {user_id}")
            # Return a dictionary
            return {
                "userId": user_id,
                "username": username,
                "password": password
            }
        else:
            logger.error(f"User creation failed! Status: {response.status_code} Body: {response.text} ")
            raise Exception(f"Failed creating user: {response.status_code}")



    def generate_token(self, username, password):
        """Generate a token for user"""
        url = f"{self.base_url}{ENDPOINTS['generate_token']}"
        payload = {"userName": username, "password": password}

        logger.info(f"Attempting to generate token for dynamic user: {username}")
        response = requests.post(url, json=payload)

        if response.status_code == 200:
            api_data = response.json()
            token = api_data.get("token")
            status = api_data.get("status")

            if token:
                masked_token = f"{token[:10]}....."
                logger.info(f"New token received: {masked_token}")

            if status == "Success":
                logger.info(f"Successfully generated user token for status: {status}")
                return token

            logger.warning(f"Token request returned status {status}")
            return None
        else:
            logger.error(f"Failed to generate user token! Status: {response.status_code}")
            raise Exception("Failed to generate user token!")


    def save_api_auth_state(self, auth_data):
        """Take API login response and builds the Playwright JSON file using absolute paths"""

        # Construct path for the .auth directory
        auth_dir = self.project_root / "framework_playwright" / "playwright" / ".auth"

        logger.info(f"Preparing to save auth state to: {auth_dir}")

        state = {
            "cookies": [
                {
                    "name": "token",
                    "value": auth_data["token"],
                    "domain": "demoqa.com",
                    "path": "/",
                    "expires": -1,
                    "httpOnly": False,
                    "secure": False,
                    "sameSite": "None",
                },
                {
                    "name": "userID",
                    "value": auth_data["userId"],
                    "domain": "demoqa.com",
                    "path": "/",
                    "expires": -1,
                    "httpOnly": False,
                    "secure": False,
                    "sameSite": "None",
                },
                {
                    "name": "userName",
                    "value": auth_data["username"],
                    "domain": "demoqa.com",
                    "path": "/",
                    "expires": -1,
                    "httpOnly": False,
                    "secure": False,
                    "sameSite": "None",
                },
                {
                    "name": "expires",
                    "value": "session",
                    "domain": "demoqa.com",
                    "path": "/",
                    "expires": -1,
                    "httpOnly": False,
                    "secure": False,
                    "sameSite": "None",
                }
            ],
            "origins": []
        }

        auth_dir.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Ensured directory exists: {auth_dir}")

        auth_path = auth_dir / "auth.json"

        try:
            with open(auth_path, "w") as f:
                json.dump(state, f)
            logger.info(f"Auth state saved: {auth_path}")

        except Exception as e:
            logger.error(f"Failed to write auth state to file: {e}")
            raise

        return auth_path

    def add_books(self, user_id, token, isbns, raise_on_failure=True):
        logger.info("Adding books to collection")
        url = f"{self.base_url}{self.endpoints['add_books']}"

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        payload = {
            "userId": user_id,
            "collectionOfIsbns": [
                {"isbn": isbn} for isbn in isbns
            ]
        }

        response = requests.post(url, json=payload, headers=headers)

        if response.status_code not in [200, 201]:
            if raise_on_failure:
                logger.error(f"Failed to add books: {response.status_code} - {response.text}")
                raise Exception("Add books failed")
            else:
                logger.info(f"Expected failure adding books: {response.status_code} - {response.text}")
                return response

        logger.info("Books added successfully")
        return response

    def delete_all_books(self, user_id, token):
        logger.info("Deleting all books from collection")

        url = f"{self.base_url}{self.endpoints['delete_books']}"

        params = {
            "UserId": user_id
        }

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        response = requests.delete(url, params=params, headers=headers)

        if response.status_code not in [200, 204]:
            logger.error(f"Failed to delete books from collection: {response.status_code} - {response.text}")
            raise Exception("Deleting books failed")

        logger.info("Books deleted from collection successfully")


    def get_user_books_map(self, user_id, token):
        logger.info("Get all books title from collection")

        url = f"{self.base_url}{self.endpoints['get_profile_books']}"

        params = {
            "UserId": user_id
        }

        headers = {
            "Authorization": f"Bearer {token}"
        }

        response = requests.get(url, params=params, headers=headers)

        if response.status_code not in [200, 304]:
            logger.error(f"Failed to get book collections: {response.status_code} - {response.text}")
            raise Exception("Get Books Collection failed")

        api_data = response.json()
        books = api_data.get("books", [])

        isbn_title_map = {
            book["isbn"]: book["title"]
            for book in books
        }

        logger.info("Book Collection received")
        return isbn_title_map


    def delete_account(self, user_id, token):
        logger.info("Deleting Account")

        endpoint = self.endpoints['delete_account']
        endpoint_with_id = endpoint.replace("{userId}", user_id)

        url = f"{self.base_url}{endpoint_with_id}"

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        response = requests.delete(url, headers=headers)

        if response.status_code != 204:
            logger.error(f"Failed to delete user: {response.status_code} - {response.text}")
            raise Exception("Failed deleting user")

        logger.info("Deleted user successfully!")
        return response

