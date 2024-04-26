import pyppeteer


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
