from openai import OpenAI
import subprocess
import base64
import os
from dotenv import load_dotenv
import json

load_dotenv()

model = OpenAI()
model.timeout = 30


def image_b64(image):
    with open(image, "rb") as f:
        return base64.b64encode(f.read()).decode()


def url2screenshot(url):
    print(f"Crawling {url}")

    if os.path.exists("screenshot.jpg"):
        os.remove("screenshot.jpg")

    result = subprocess.run(
        ["node", "screenshot.js", url],
        capture_output=True,
        text=True
    )

    exitcode = result.returncode
    output = result.stdout

    if not os.path.exists("screenshot.jpg"):
        print("ERROR1")
        return "Failed to scrape the website"

    b64_image = image_b64("screenshot.jpg")
    return b64_image


def visionExtract(b64_image, prompt):
    response = model.chat.completions.create(
        model="gpt-4-vision-preview",
        messages=[
            {
                "role": "system",
                "content": "You a web scraper, your job is to extract information based on a screenshot of a website & user's instruction",
            }
        ]
        + [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": f"data:image/jpeg;base64,{b64_image}",
                    },
                    {
                        "type": "text",
                        "text": prompt,
                    },
                ],
            }
        ],
        max_tokens=1024,
    )

    message = response.choices[0].message
    message_text = message.content

    if "ANSWER_NOT_FOUND" in message_text:
        print("ERROR2: Answer not found")
        return (
            "I was unable to find the answer on that website. Please pick another one"
        )
    else:
        print(f"GPT: {message_text}")
        return message_text


def visionExtract2(b64_image, prompt):
    system_prompt = """
    You a web scraper, your job is to extract information based on a screenshot of a website & user's instruction

    Respond only with JSON. Do not include backticks (example ```json). The JSON should be in the format:

    {"value":<insert the answer to the user's question. Value should work with python's `int()` function>, "comment":<insert any comments you have per the user's question as text here>"}

    Ensure that the JSON is valid json and will work with python's `json.loads` method
"""
    response = model.chat.completions.create(
        model="gpt-4-vision-preview",
        messages=[
            {
                "role": "system",
                "content": system_prompt,
            }
        ]
        + [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": f"data:image/jpeg;base64,{b64_image}",
                    },
                    {
                        "type": "text",
                        "text": prompt,
                    },
                ],
            }
        ],
        max_tokens=1024,
    )

    message = response.choices[0].message
    message_text = message.content
    print(f"message_text {message_text}")

    if "ANSWER_NOT_FOUND" in message_text:
        print("ERROR2: Answer not found")
        return (
            "I was unable to find the answer on that website. Please pick another one"
        )

    message_json = json.loads(message_text)
    return message_json["value"], message_json["comment"]


def visionCrawl(url, prompt):
    b64_image = url2screenshot(url)

    print("Image captured")

    if b64_image == "Failed to scrape the website":
        return "I was unable to crawl that site. Please pick a different one."
    else:
        return visionExtract(b64_image, prompt)


def visionCrawl2(url, prompt):
    b64_image = url2screenshot(url)

    print("Image captured")

    if b64_image == "Failed to scrape the website":
        return "I was unable to crawl that site. Please pick a different one."
    else:
        return visionExtract2(b64_image, prompt)


if __name__ == "__main__":
    response = visionCrawl(
        "https://www.linkedin.com/in/shaheenghiassy/",
        "Extract the user's work experience",
    )
    print(response)
