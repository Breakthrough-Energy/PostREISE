const { SCREENSHOT_COMPARISON_CONFIG } = require('../util');
const { saveVideo } = require('playwright-video');

const TIMEOUT = 150000;

beforeEach(async () => {
  await jestPlaywright.resetContext();
  page.setDefaultTimeout(0); // Click actions, etc. do not time out
});

describe.jestPlaywrightSkip({ browsers: ['firefox', 'webkit'] }, 'Dashboard', () => {
  test('Dashboard loads all graphs', async () => {
    await page.goto(`${process.env.SITE_URL}/dashboard`, { waitUntil: 'networkidle' });

    const image = await page.screenshot({ fullPage: true });
    expect(image).toMatchImageSnapshot(SCREENSHOT_COMPARISON_CONFIG);
  }, TIMEOUT);

  test('Dashboard loads multiple scenarios from query params', async () => {
    await page.goto(`${process.env.SITE_URL}/dashboard?scenarioId=s1270%2Cs1204`, { waitUntil: 'networkidle' });

    const image = await page.screenshot({ fullPage: true });
    expect(image).toMatchImageSnapshot(SCREENSHOT_COMPARISON_CONFIG);
  }, TIMEOUT);


  // Interactions
  test('Dashboard changes scenario', async () => {
    await page.goto(`${process.env.SITE_URL}/dashboard`);
    await page.click('.scenario-toolbar__select');
    await page.click('text=Independent, USA 2030 (extra renewables)');

    const image = await page.screenshot({ fullPage: true });
    expect(image).toMatchImageSnapshot(SCREENSHOT_COMPARISON_CONFIG);
  }, TIMEOUT);

  test('Dashboard adds graph columns', async () => {
    await page.goto(`${process.env.SITE_URL}/dashboard`);
    await page.click('text=+');

    const image = await page.screenshot({ fullPage: true });
    expect(image).toMatchImageSnapshot(SCREENSHOT_COMPARISON_CONFIG);
  }, TIMEOUT);

  test('Dashboard removes graph columns', async () => {
    await page.goto(`${process.env.SITE_URL}/dashboard?scenarioId=s1270%2Cs1204`);
    await page.click('.graph-column__close');

    const image = await page.screenshot({ fullPage: true });
    expect(image).toMatchImageSnapshot(SCREENSHOT_COMPARISON_CONFIG);
  }, TIMEOUT);

  test('Dashboard changes location', async () => {
    await page.goto(`${process.env.SITE_URL}/dashboard`);
    await page.click('.scenario-toolbar__location-select');
    await page.click('text=California');
    await page.waitForTimeout(2000); // Wait for built in transition time

    const image = await page.screenshot({ fullPage: true });
    expect(image).toMatchImageSnapshot(SCREENSHOT_COMPARISON_CONFIG);
  }, TIMEOUT);

  test('Moving the mouse over a location highlights that state', async () => {
    await page.goto(`${process.env.SITE_URL}/dashboard`);
    await page.hover('.graph');

    const image = await page.screenshot({ fullPage: true });
    expect(image).toMatchImageSnapshot(SCREENSHOT_COMPARISON_CONFIG);
  }, TIMEOUT);

  test('can toggle other branch graphs', async () => {
    await page.goto(`${process.env.SITE_URL}/dashboard`);
    await page.click(':nth-match(.dashboard-graph__toggle-button, 2)'); // Risk graph
    await page.waitForTimeout(2000); // Wait for built in transition time

    const image = await page.screenshot({ fullPage: true });
    expect(image).toMatchImageSnapshot(SCREENSHOT_COMPARISON_CONFIG);
  }, TIMEOUT);
});