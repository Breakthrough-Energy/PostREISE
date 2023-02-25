## Running Playwright tests

We currently use Playwright for more maintainable integration tests:
https://playwright.dev/\
In addition to Playwright, we use Jest as the testrunner as outlined in these blog posts:
https://medium.com/geekculture/dockerizing-playwright-e2e-tests-c041fede3186
https://www.carlrippon.com/getting-started-with-playwright/

Compared to Selenium, Playwright is generally less flaky, requires less configuration than Selenium, and can test using webkit (Safari) browsers. We use the prebuilt image `mcr.microsoft.com/playwright:bionic` as the base image, where we run the test code within the container while loading an external website address to allow for greater flexibility such as testing website locally, within other containers, and also on the deployed website.

### To run the tests:
1. Define an environment variable `SITE_URL` to be the base website URL for testing
2. Make sure you are within the `integration_tests/playwright` directory, then run the command:
`docker-compose run playwright yarn test`

### Tips
- To enable/disable debug mode, uncomment the DEBUG line in `integration_tests/playwright/docker-compose.yml`.
- Currently, the easiest way to run a single test suite is to edit `testMatch` in `integration_tests/playwright/tests/jest.e2e.config.js`.