from openai import OpenAI
import json

model = OpenAI()
model.timeout = 30

messages = [
    {
        "role": "system",
        "content": """
            You are a spreadsheet analyst who can browse the web and answer user questions to fill in values for specific spreadsheet cells. You will be given instructions on what to do by browsing. You are connected to a web browser and you will be given the screenshot of the website you are on. The links on the website will be highlighted in red in the screenshot. Always read what is in the screenshot. Don't guess link names.

            You can go to a specific URL by answering with the following JSON format:
            {"url": "url goes here"}
            Make sure your JSON works with python's json.loads method

            You can click links on the website by referencing the text inside of the link/button, by answering in the following JSON format:
            {"click": "Text in link"}
            Make sure your JSON works with python's json.loads method

            Once you are on a URL and you have found the answer to the user's question, you can answer in the following JSON format:
            {"value": "Specific value to the user's question", "comment":"Any additional information you want to give the user"}
            Make sure your JSON works with python's json.loads method

            Use google search by set a sub-page like 'https://google.com/search?q=search' if applicable. Prefer to use Google for simple queries.
            If the user wants information about a noun use wikipedia at 'https://en.wikipedia.org/wiki/Main_Page'
            If the user provides a direct URL, go to that one. Do not make up links
            """,
    }
]


def append(message):
    messages.append(
        {
            "role": "user",
            "content": message,
        }
    )


def append_image(message, base64_image):
    messages.append(
        {
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": f"data:image/jpeg;base64,{base64_image}",
                },
                {
                    "type": "text",
                    "text": message,
                },
            ],
        }
    )


async def get_json_response():
    response = model.chat.completions.create(
        model="gpt-4-vision-preview",
        max_tokens=1024,
        messages=messages,
    )

    message = response.choices[0].message
    message_text = message.content

    messages.append(
        {
            "role": "assistant",
            "content": message_text,
        }
    )

    try:
        message_json = json.loads(message_text)
        return message_json
    except Exception:
        messages.append(
            {
                "role": "user",
                "content": "ERROR: The JSON you provided threw an exception using python's json.load method. Please reevalute this JSON and provide a correctly formatted value: {message_text}",
            }
        )
        return await get_json_response()
