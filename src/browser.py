import asyncio
import pyppeteer
import base64

timeout = 14000


class Browser(object):
    def __init__(self, browser, page):
        self.browser = browser
        self.page = page

    async def take_screenshot(self):
        await self.page.screenshot(
            {
                "path": "screenshot.jpg",
                "fullPage": False,
            }
        )

        with open("screenshot.jpg", "rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode("utf-8")

        return base64_image

    async def navigate(self, url):
        await self.page.goto(
            url,
            {
                "waitUntil": "domcontentloaded",
                "timeout": timeout,
            },
        )

        await asyncio.sleep(timeout / 10000)  # Convert milliseconds to seconds

    async def click_link(self, link_text):
        elements = await self.page.querySelectorAll("[gpt-link-text]")

        partial = None
        exact = None

        for element in elements:
            attribute_value = await self.page.evaluate(
                '(el) => el.getAttribute("gpt-link-text")', element
            )

            if link_text in attribute_value:
                partial = element

            if attribute_value == link_text:
                exact = element

        if exact or partial:
            navigation_task = asyncio.create_task(
                self.page.waitForNavigation(waitUntil="domcontentloaded")
            )
            click_task = asyncio.create_task((exact or partial).click())

            await click_task
            await navigation_task

            await asyncio.sleep(timeout / 10000)  # Convert milliseconds to seconds

            await self.highlight_links()
        else:
            raise Exception("Can't find link")

    async def highlight_links(self):
        await self.page.evaluate(
            """() => {
            document.querySelectorAll('[gpt-link-text]').forEach(e => {
                e.removeAttribute("gpt-link-text");
            });
        }"""
        )

        elements = await self.page.querySelectorAll(
            "a, button, input, textarea, [role=button], [role=treeitem]"
        )

        for element in elements:
            await self.page.evaluate(
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


async def init_browser() -> Browser:
    """
    Needed an asynchrous constructor for the Browser class.
    This is how the internet told me to do it in python
    """
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

    return Browser(browser, page)
