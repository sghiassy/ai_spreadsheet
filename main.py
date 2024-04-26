import re
import src.ai as ai
import base64
import asyncio
import src.browser
import src.google_sheet as google_sheet
import time

from dotenv import load_dotenv
import json
import requests

load_dotenv()


timeout = 14000
COMMENT_FIELDS = "id, anchor, content, modifiedTime, quotedFileContent, author(displayName), replies(id,content,modifiedTime, author(displayName)), createdTime, htmlContent, kind, deleted, resolved"

# If modifying these scopes, delete the file token.json.


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


def get_comments(drive_service):
    comments_data = (
            drive_service.comments()
            .get(fileId=SPREADSHEET_ID, commentId="AAABLNjT_20", fields=COMMENT_FIELDS)
            .execute()
        )
    return comments_data


def add_comment(drive_service):
    """
    Comments attached to cell: https://www.youtube.com/live/ZBU52nacbLw?si=MTud8YGjvy1WFKxG&t=325
    """
    reply = (
            drive_service.replies()
            .create(
                fileId=SPREADSHEET_ID,
                commentId="AAABLNjT_20",
                body=dict(kind="drive#reply", content="I am the content"),
                fields="id, content, modifiedTime",
            )
            .execute()
        )
    return reply


def create_note(sheets_service):
    body = {
        "requests": [
            {
                "repeatCell": {
                    "range": {
                        "sheetId": 0,  # this is the end bit of the url
                        "startRowIndex": 0,
                        "endRowIndex": 1,
                        "startColumnIndex": 0,
                        "endColumnIndex": 1,
                    },
                    "cell": {"note": "Hey, I'm a comment!"},
                    "fields": "note",
                }
            }
        ]
    }
    result = (
        sheets_service.spreadsheets()
        .batchUpdate(spreadsheetId=SPREADSHEET_ID, body=body)
        .execute()
    )
    return result


async def highlight_links(page):
    await page.evaluate(
        """() => {
        document.querySelectorAll('[gpt-link-text]').forEach(e => {
            e.removeAttribute("gpt-link-text");
        });
    }"""
    )

    elements = await page.querySelectorAll(
        "a, button, input, textarea, [role=button], [role=treeitem]"
    )

    for element in elements:
        await page.evaluate(
            """(e) => {
            function isElementVisible(el) {
                if (!el) return false; // Element does not exist

                function isStyleVisible(el) {
                    const style = window.getComputedStyle(el);
                    return style.width !== '0' &&
                           style.height !== '0' &&
                           style.opacity !== '0' &&
                           style.display !== 'none' &&
                           style.visibility !== 'hidden';
                }

                function isElementInViewport(el) {
                    const rect = el.getBoundingClientRect();
                    return (
                    rect.top >= 0 &&
                    rect.left >= 0 &&
                    rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
                    rect.right <= (window.innerWidth || document.documentElement.clientWidth)
                    );
                }

                // Check if the element is visible style-wise
                if (!isStyleVisible(el)) {
                    return false;
                }

                // Traverse up the DOM and check if any ancestor element is hidden
                let parent = el;
                while (parent) {
                    if (!isStyleVisible(parent)) {
                    return false;
                    }
                    parent = parent.parentElement;
                }

                // Finally, check if the element is within the viewport
                return isElementInViewport(el);
            }

            e.style.border = "1px solid red";

            const position = e.getBoundingClientRect();

            if( position.width > 5 && position.height > 5 && isElementVisible(e) ) {
                const link_text = e.textContent.replace(/[^a-zA-Z0-9 ]/g, '');
                e.setAttribute( "gpt-link-text", link_text );
            }
        }""",
            element,
        )


async def main():

    page = await src.browser.init_browser()

    wks = google_sheet.get_worksheet('Sheet6')

    active_cells = google_sheet.get_active_cells(wks)

    for cell in active_cells:
        cell_ref = cell[0]  # i.e: A1, D7, etc
        cell_text = cell[1]
        cell_note = wks.get_note(cell_ref)
        print(f"cell_note: {cell_note}")

        if not cell_note:
            continue

        if not cell_text == "-":
            continue

        ai.append(cell_note)

        url = None
        screenshot_taken = False

        while True:
            if url:
                print("Crawling " + url)
                await page.goto(url, {
                    'waitUntil': "domcontentloaded",
                    'timeout': timeout,
                })

                await asyncio.sleep(timeout / 10000)  # Convert milliseconds to seconds

                # Assuming highlight_links is a defined function
                await highlight_links(page)

                screenshot_taken = True
                url = None

            if screenshot_taken:
                screenshot = await src.browser.take_screenshot(page)

                ai.append_image(
                    'Here\'s the screenshot of the website you are on right now. You can click on links with {"click": "Link text"} or you can crawl to another URL if this one is incorrect. If you find the answer to the user\'s question, you can respond normally.',
                    screenshot,
                )

                screenshot_taken = False

            message_text = await ai.get_response()

            print("GPT: " + message_text)

            if '{"click": "' in message_text:
                parts = message_text.split('{"click": "')
                parts = parts[1].split('"}')
                link_text = re.sub(r'[^a-zA-Z0-9 ]', '', parts[0])

                print("Clicking on " + link_text)

                try:
                    elements = await page.querySelectorAll('[gpt-link-text]')

                    partial = None
                    exact = None

                    for element in elements:
                        attribute_value = await page.evaluate('(el) => el.getAttribute("gpt-link-text")', element)

                        if link_text in attribute_value:
                            partial = element

                        if attribute_value == link_text:
                            exact = element

                    if exact or partial:
                        navigation_task = asyncio.create_task(page.waitForNavigation(waitUntil='domcontentloaded'))
                        click_task = asyncio.create_task((exact or partial).click())

                        await click_task
                        await navigation_task

                        # response, _ = await asyncio.gather(navigation_task, click_task)

                        await asyncio.sleep(
                            timeout / 10000
                        )  # Convert milliseconds to seconds

                        await highlight_links(page)

                        await page.screenshot({
                            'path': "screenshot.jpg",
                            'quality': 100,
                            'fullPage': True
                        })

                        screenshot_taken = True
                    else:
                        raise Exception("Can't find link")
                except Exception as error:
                    print("ERROR: Clicking failed", error)

                    ai.messages.append({
                        "role": "user",
                        "content": "ERROR: I was unable to click that element",
                    })

                continue
            elif '{"url": "' in message_text:
                parts = message_text.split('{"url": "')
                parts = parts[1].split('"}')
                url = parts[0]
                continue
            else:
                print(f"message_text: {message_text}")
                try:
                    message_json = json.loads(message_text)
                    if "value" in message_json:
                        wks.update_acell(cell_ref, message_json['value'])

                    # if "comment" in message_json:
                    #     wks.update_note(cell_ref, cell_note + "\n\n" + message_json["comment"] + "\n---")
                except Exception as e:
                    print(f"message didn't work {e}")
                break


if __name__ == "__main__":
    while True:
        asyncio.get_event_loop().run_until_complete(main())
        time.sleep(10)  # Wait for 10 seconds
