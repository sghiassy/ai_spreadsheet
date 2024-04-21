const puppeteer = require('puppeteer-extra');
const StealthPlugin = require('puppeteer-extra-plugin-stealth');
puppeteer.use(StealthPlugin());

const url =
  process.argv[2] ||
  "https://docs.google.com/spreadsheets/d/1j33HzZx4SyhOudVbFBc5Uo1d5VKwvHAjCIw60fQmIjU/edit?usp=sharing";
const timeout = 5000;

(async () => {

    const browser = await puppeteer.connect({
      browserURL: "http://localhost:9222",
      defaultViewport: null,
    });

    const page = await browser.newPage();

    await page.setViewport( {
        width: 1200,
        height: 1200,
        deviceScaleFactor: 1,
    } );

    await page.goto( url, {
        waitUntil: "domcontentloaded",
        timeout: timeout,
    } );

    await page.waitForTimeout(timeout);

    await page.screenshot({
        path: "screenshot.jpg",
        fullPage: true,
    });

    await browser.close();
})();
