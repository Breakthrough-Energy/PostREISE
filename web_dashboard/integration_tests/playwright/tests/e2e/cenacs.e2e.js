const { saveVideo } = require('playwright-video');

beforeEach(async () => {
    await jestPlaywright.resetContext()
});

describe('Homepage', () => {
    test('Homepage loads all Bokeh graphs', async () => {
        await page.goto(`${process.env.SITE_URL}`)

        await page.waitForFunction(() => Object.keys(window.Bokeh.index).length > 3);
        indexLength = await page.evaluate(() => Object.keys(window.Bokeh.index).length)
        expect(indexLength).toEqual(4)
    }, 30000);
});