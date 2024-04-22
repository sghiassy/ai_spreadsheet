import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from openai import OpenAI
from dotenv import load_dotenv
import json
import requests
from vison_scraper import visionCrawl2

load_dotenv()

model = OpenAI()
model.timeout = 30

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

# The ID and range of a sample spreadsheet.
SPREADSHEET_ID = "18_0zVG1l3-HIhPwvSuONZxqwrjOCRN2JYhiiByi06_s"
RANGE = "Sheet1!D7"


def increment_cell(service):
    # Call the Sheets API
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=RANGE).execute()
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
        spreadsheetId=SPREADSHEET_ID, range=RANGE,
        valueInputOption="USER_ENTERED", body=body).execute()


def update_cell(service, new_value):
    body = {"values": [[new_value]]}
    result = (
        service.spreadsheets()
        .values()
        .update(
            spreadsheetId=SPREADSHEET_ID,
            range=RANGE,
            valueInputOption="USER_ENTERED",
            body=body,
        )
        .execute()
    )
    print(f"result: {result}")


def get_note(service):
    request = service.spreadsheets().get(
        spreadsheetId=SPREADSHEET_ID, ranges=RANGE, includeGridData=True
    )
    response = request.execute()

    # Get the notes (comments) from the cell
    cell_data = response['sheets'][0]['data'][0]['rowData'][0]['values'][0]
    if 'note' in cell_data:
        # print(cell_data['note'])
        return cell_data['note']
    else:
        return ''
        # print('No comments in cell D7')


def update_note(service, new_note, prev_note):
    request = service.spreadsheets().batchUpdate(
        spreadsheetId=SPREADSHEET_ID,
        body={
            "requests": [
                {
                    "updateCells": {
                        "range": {
                            "sheetId": 0,  # Assuming the sheet ID is 0
                            "startRowIndex": 6,  # 0-based, so 6 is row 7
                            "endRowIndex": 7,
                            "startColumnIndex": 3,  # 0-based, so 3 is column D
                            "endColumnIndex": 4,
                        },
                        "rows": [{"values": [{"note": prev_note + "\n" + new_note}]}],
                        "fields": "note",
                    }
                }
            ]
        },
    )
    response = request.execute()
    return response


def decipher_message(note):

    prompt = """
    You are a Google Sheets expert. A user will attach a note to a cell, and your job will be to extract two pieces of information from it 1.) Extract the url and 2.) The prompt.

    Respond only with JSON. The JSON should be in the format:

    {"url":<insert url here>, "prompt":<the message with the url removed>}

    Ensure that the JSON is valid json and will work with python's `json.loads` method
"""

    response = model.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {
                "role": "system",
                "content": prompt,
            },
            {
                "role": "user",
                "content": note,
            },
        ],
        max_tokens=1024,
    )

    message = response.choices[0].message
    message_text = message.content
    print(f"message_text {message_text}")
    message_json = json.loads(message_text)
    return message_json["url"], message_json['prompt']


def fetch_webpage(url):
    response = requests.get(url)
    response.raise_for_status()  # Raise an exception if the request was unsuccessful
    return response.text


def scrape_web(url, user_prompt):
    system_prompt = """
    You are an expert web scraper. You will get the contents from a webpage and a question from the user.

    Your goal is to answer the user's question with a number given the contents of the webpage.

    You will be given information in the form of json, with the user's question in the field `question_from_user` and the relevant website information in the field `website_text`

    Respond only with JSON. The JSON should be in the format:

    {"value":<insert the answer to the user's question. Value should work with python's `int()` function>, "comment":<insert any comments you have per the user's question as text here"}

    Ensure that the JSON is valid json and will work with python's `json.loads` method
"""

    webpage = fetch_webpage(url)

    prompt = {"question_from_user": user_prompt, "website_text": webpage}

    response = model.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        max_tokens=1024,
    )

    message = response.choices[0].message
    message_text = message.content
    print(f"message_text {message_text}")
    message_json = json.loads(message_text)
    return message_json["value"], message_json["comment"]


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
        increment_cell(service)
        note = get_note(service)
        url, prompt = decipher_message(note)
        value, ai_comment = visionCrawl2(url, prompt)
        update_cell(service, value)
        update_note(service, ai_comment, note)

        # value, comment = scrape_web(url, prompt)
        # print(f"value{value} comment{comment}")

    except HttpError as err:
        print(err)


if __name__ == "__main__":
    main()
