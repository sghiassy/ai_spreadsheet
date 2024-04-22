import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = "18_0zVG1l3-HIhPwvSuONZxqwrjOCRN2JYhiiByi06_s"
SAMPLE_RANGE_NAME = "Class Data!A2:E"


def main():
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("oauth.json", SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    try:
        service = build("sheets", "v4", credentials=creds)

        # Call the Sheets API
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID, range="Sheet1!D7").execute()
        values = result.get("values", [])

        # Remove commas from the value
        clean_value = values[0][0].replace(',', '') if values else '0'

        # Increment the value by 1
        new_value = int(clean_value) + 1

        # Update cell D7 with the new value
        body = {
            'values': [[new_value]]
        }
        result = service.spreadsheets().values().update(
            spreadsheetId=SAMPLE_SPREADSHEET_ID, range="Sheet1!D7",
            valueInputOption="USER_ENTERED", body=body).execute()
    except HttpError as err:
        print(err)


if __name__ == "__main__":
    main()
