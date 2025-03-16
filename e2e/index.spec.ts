import { test, expect } from '@playwright/test';

test('page contains name', async ({ page }) => {
  await page.goto('http://localhost');

  const name = page.getByText('Jonathan Frankel');
  await expect(name).toBeVisible();
});

test('web counter exists', async ({ page }) => {
  await page.goto('http://localhost');

  // wait for network
  await page.waitForLoadState('networkidle');

  const counter = page.getByText(/Web counter: \d+ site visits/);
  await expect(counter).toBeVisible();
});
