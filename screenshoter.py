import asyncio
import pyppeteer

timeout = 5000


async def screenshot(url):
    # browser = await launch(headless=False)
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

    await page.goto(
        url,
        {
            "waitUntil": "domcontentloaded",
            "timeout": timeout,
        },
    )

    await asyncio.sleep(timeout / 10000)  # Convert milliseconds to seconds

    await page.screenshot(
        {
            "path": "screenshot.jpg",
            "fullPage": True,
        }
    )

    await browser.close()


if __name__ == "__main__":
    asyncio.run(screenshot("https://www.salesforce.com//products/sales-pricing/"))
