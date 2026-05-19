import { test, expect } from '@playwright/test';

// MiniStack S3 static site using path-style URLs (aws:s3UsePathStyle: true in Pulumi.local.yaml)
const ministackUrl = 'http://localhost:4566/resume-local.frankel.test/index.html';

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
