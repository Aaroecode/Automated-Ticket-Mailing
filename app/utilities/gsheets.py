
import os

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.auth import exceptions as gsheetexceptions
from app.utilities.clogging import get_logger

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

gsheet_logger = get_logger("GSHEETS")

class Gsheets():
    def __init__(self, sheetID: str):
        self.creds = None
        self.sheetID = sheetID
        self.scope = ["https://www.googleapis.com/auth/spreadsheets"]
        self.token_path = os.path.join(os.getcwd(), "app", "assets","gsheet-creds", "token.json")
        self.creds_path = os.path.join(os.getcwd(), "app", "assets", "gsheet-creds", "credentials.json")
        if os.path.exists(self.token_path):
            self.creds = Credentials.from_authorized_user_file(self.token_path, scopes=self.scope)
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                try: 
                    self.creds.refresh(Request())
                except:
                    os.remove(self.token_path)
                    
            else:
                self.flow = InstalledAppFlow.from_client_secrets_file(self.creds_path, scopes=self.scope)
                self.creds = self.flow.run_local_server(port=0, open_browser=False)
            with open(self.token_path, "w") as token:
                token.write(self.creds.to_json())
        

        try:
            service = build("sheets", "v4", credentials=self.creds)
            self.sheet = service.spreadsheets()
        except HttpError as err:
            print(err)

    def get(self, range: str):
        response = (self.sheet.values().get(spreadsheetId = self.sheetID, range=range).execute())
        values = response.get("values", [])
        return values[0]
    
    def append(self, data: list):
        if isinstance(data[0], str):
            temp = []
            temp.append(data)
            data = temp
        body = {"values": data}
        while True:
            try:
                response = self.sheet.values().append(spreadsheetId = self.sheetID, range= "Sheet1!A1", body =body, valueInputOption = "RAW").execute()
                break
            except:
                gsheet_logger.log(20, self.creds)
                if self.creds and self.creds.expired and self.creds.refresh_token:
                    self.creds.refresh(Request())
                else:
                    self.flow = InstalledAppFlow.from_client_secrets_file(self.creds_path, scopes=self.scope)
                    creds = self.flow.run_local_server(port=0)
                with open(self.token_path, "w") as token:
                    token.write(creds.to_json())