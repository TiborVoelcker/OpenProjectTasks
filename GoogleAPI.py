from __future__ import print_function

import logging
import os.path

from google.auth.exceptions import RefreshError
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from oauthlib.oauth2.rfc6749.errors import OAuth2Error
from telegram_utils import TelegramBot

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/tasks"]

basepath = os.path.dirname(os.path.realpath(__file__))


def new_token():
    flow = InstalledAppFlow.from_client_secrets_file("Resources/credentials.json", SCOPES)
    flow.redirect_uri = "urn:ietf:wg:oauth:2.0:oob"
    url, _ = flow.authorization_url(prompt="consent")
    bot = TelegramBot()
    bot.send_message(
        "Your Google API token run out. Please [reauthenticate the app]"
        f"({url}) and send the code back.",
        parse_mode="Markdown",
    )

    @bot.get_message
    def handle_code(msg):
        try:
            flow.fetch_token(code=msg.text)
        except OAuth2Error:
            return False
        if flow.credentials and flow.credentials.valid:
            return True

    handle_code()
    return flow.credentials


def create_service():
    """Shows basic usage of the Tasks API.
    Prints the title and ID of the first 10 task lists.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    logger = logging.getLogger(__name__)
    filepath = os.path.join(basepath, "Resources/token.json")
    if os.path.exists(filepath):
        creds = Credentials.from_authorized_user_file(filepath, SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                logger.debug("Using Refresh token.")
                creds.refresh(Request())
            except RefreshError:
                logger.info("Asking for new authentication...")
                creds = new_token()
                logger.info("Authentication complete!")
        else:
            logger.info("No token. Asking for authentication...")
            creds = new_token()
            logger.info("Authentication complete!")
        # Save the credentials for the next run
        with open(filepath, "w") as token:
            token.write(creds.to_json())

    return build("tasks", "v1", credentials=creds)
