import { test, expect } from "@playwright/test";

test.describe("Open Homepage", () => {
  test("displays a correct page title", async ({ browser }) => {
    const page = await browser.newPage();
    await page.setExtraHTTPHeaders({
      "X-Auth-Token": process.env.SSO_AUTH_TOKEN || "",
    });
    await page.goto(`http://0.0.0.0:${process.env.PORT}`);
    await expect(page).toHaveTitle("Websites Content System");
  });
});
