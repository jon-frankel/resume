import { test, expect } from '@playwright/test';

// Ministack does not actually return the URL for the s3 site, but this it.
const ministackUrl = 'http://resume-local.frankel.test.s3-website.localhost:4566/index.html';

const host = process.env.URL ?? ministackUrl;
console.log("Testing host: ", host);

test('page contains name', async ({ page }) => {
  await page.goto(host);

  const name = page.getByText('Jonathan Frankel');
  await expect(name).toBeVisible();
});

test('web counter exists', async ({ page }) => {
  await page.goto(host);

  // wait for network idle to ensure the counter has been updated
  await page.waitForLoadState('networkidle');

  const counter = page.getByText(/Web counter: \d+ site visits/);
  await expect(counter).toBeVisible();
});
