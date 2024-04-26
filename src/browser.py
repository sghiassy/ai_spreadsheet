import asyncio
import pyppeteer
import base64

timeout = 14000


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


async def click_link(page, link_text):
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


        else:
            raise Exception("Can't find link")
    except Exception as error:
        print("ERROR: Clicking failed", error)

        ai.messages.append({
            "role": "user",
            "content": "ERROR: I was unable to click that element",
        })
