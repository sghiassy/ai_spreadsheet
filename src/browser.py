import pyppeteer
import base64


async def init_browser():
    browser = await pyppeteer.connect(
        browserURL="http://localhost:9222", defaultViewport=None
    )

    page = await browser.newPage()

    await page.setViewport(
        {
            "width": 1200,
            "height": 1200,
            "deviceScaleFactor": 1,
        }
    )

    return page


async def take_screenshot(page):
    await page.screenshot(
        {
            "path": "screenshot.jpg",
            "fullPage": False,
        }
    )

    with open("screenshot.jpg", "rb") as image_file:
        base64_image = base64.b64encode(image_file.read()).decode("utf-8")

    return base64_image
