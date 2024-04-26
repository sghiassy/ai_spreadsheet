import asyncio
import src.browser
import src.google_sheet as google_sheet
import src.ai as ai
import time
from dotenv import load_dotenv
import json

load_dotenv()


async def main():

    browser = await src.browser.init_browser()

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
                await browser.navigate(url)
                await browser.highlight_links()
                screenshot_taken = True
                url = None

            if screenshot_taken:
                screenshot = await browser.take_screenshot()

                ai.append_image(
                    'Here\'s the screenshot of the website you are on right now. You can click on links with {"click": "Link text"} or you can crawl to another URL if this one is incorrect. If you find the answer to the user\'s question, you can respond normally.',
                    screenshot,
                )

                screenshot_taken = False

            message_json = await ai.get_json_response()

            print("GPT: " + json.dumps(message_json))

            if 'click' in message_json:
                link_text = message_json['click']

                print("Clicking on " + link_text)

                try:
                    await browser.click_link(link_text)
                    await browser.take_screenshot()

                    screenshot_taken = True
                except Exception as e:
                    ai.append(
                        f"ERROR: I was unable to click that element. Here's the exception that occured {e}",
                    )
                continue
            elif 'url' in message_json:
                url = message_json['url']
                continue
            elif 'value' in message_json:
                wks.update_acell(cell_ref, message_json['value'])
                continue
            else:
                print("ERROR 65rfd: Unknown entries in JSON")


if __name__ == "__main__":
    while True:
        asyncio.get_event_loop().run_until_complete(main())
        time.sleep(10)  # Wait for 10 seconds
