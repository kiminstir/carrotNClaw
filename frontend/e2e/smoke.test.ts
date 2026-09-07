import { expect, test } from '@playwright/test';

test('home renders CMS content', async ({ page }) => {
	await page.goto('/');
	await expect(page.getByRole('heading', { level: 1 })).toContainText('Carrot&Claw');
	await expect(page.getByRole('navigation', { name: 'Main' }).first()).toContainText('About');
});

test('navigation is client-side so the layout (and audio player) persists', async ({ page }) => {
	await page.goto('/');
	await page
		.locator('header')
		.first()
		.evaluate((el) => el.setAttribute('data-marker', 'kept'));
	await page
		.getByRole('navigation', { name: 'Main' })
		.first()
		.getByRole('link', { name: 'About' })
		.click();
	await expect(page).toHaveURL(/\/about\/?$/);
	await expect(page.getByRole('heading', { level: 1 })).toContainText('About');
	await expect(page.locator('header').first()).toHaveAttribute('data-marker', 'kept');
});

test('unknown page shows 404', async ({ page }) => {
	const response = await page.goto('/does-not-exist/');
	expect(response?.status()).toBe(404);
	await expect(page.getByRole('heading', { level: 1 })).toContainText('404');
});
