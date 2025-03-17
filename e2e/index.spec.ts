import { test, expect } from '@playwright/test';

const host = process.env.URL ?? 'http://localhost';
console.log("Testing host: ", host);

test('page contains name', async ({ page }) => {
  await page.goto(host);

  const name = page.getByText('Jonathan Frankel');
  await expect(name).toBeVisible();
});

test('web counter exists', async ({ page }) => {
  await page.goto(host);

  // wait for network
  await page.waitForLoadState('networkidle');

  const counter = page.getByText(/Web counter: \d+ site visits/);
  await expect(counter).toBeVisible();
});
