import { expect, test } from '@playwright/test';

test('home renders CMS content', async ({ page }) => {
	await page.goto('/');
	await expect(page.getByRole('heading', { level: 1 })).toContainText('Carrot&Claw');
	await expect(page.getByRole('navigation', { name: 'Main' }).first()).toContainText('About');
});

test('hero drifts lantern motes and leans its branches toward the pointer', async ({ page }) => {
	await page.goto('/');
	const hero = page.locator('.tavern-hero');
	await expect(hero.locator('.mote')).toHaveCount(22);
	await hero.hover({ position: { x: 10, y: 10 } });
	await expect(hero).toHaveAttribute('style', /--tilt-x: -0\.\d+; --tilt-y: -0\.\d+/);
	await page.mouse.move(0, 0); // leaves the hero (the header is in the way)
	await expect(hero).toHaveAttribute('style', /--tilt-x: 0; --tilt-y: 0/);
});

test.describe('reduced motion', () => {
	test.use({ reducedMotion: 'reduce' });

	test('hero keeps still: no motes, no tilt', async ({ page }) => {
		await page.goto('/');
		const hero = page.locator('.tavern-hero');
		await expect(hero.locator('.hero-motes')).toBeHidden();
		await hero.hover({ position: { x: 10, y: 10 } });
		await expect(hero).not.toHaveAttribute('style', /--tilt-x/);
	});
});

test('scroll vine grows down the gutter and sprouts leaves as the page scrolls', async ({
	page
}) => {
	await page.setViewportSize({ width: 1440, height: 900 });
	await page.goto('/menu/');
	const vine = page.getByTestId('scroll-vine');
	await expect(vine).toBeVisible();
	const stem = vine.locator('.vine-stem');
	const dashOffset = () => stem.evaluate((el) => parseFloat(getComputedStyle(el).strokeDashoffset));
	await expect.poll(dashOffset).toBeGreaterThan(0);
	const offsetAtTop = await dashOffset();
	const grownAtTop = await vine.locator('.vine-leaf.is-grown').count();

	await page.evaluate(() => window.scrollTo(0, 3000));
	await expect.poll(dashOffset).toBeLessThan(offsetAtTop);
	expect(await vine.locator('.vine-leaf.is-grown').count()).toBeGreaterThan(grownAtTop);
});

test('scroll vine stays out of the way on narrow screens', async ({ page }) => {
	await page.setViewportSize({ width: 390, height: 844 });
	await page.goto('/menu/');
	await expect(page.getByTestId('scroll-vine')).toBeHidden();
});

test('bard sign player shows its controls and a resting equalizer', async ({ page }) => {
	await page.goto('/');
	const player = page.getByTestId('audio-player');
	await expect(player).toBeVisible();
	await expect(player.locator('.eq-bar')).toHaveCount(4);
	await expect(player.getByRole('button', { name: 'Play music' })).toBeVisible();
	await expect(player.getByRole('button', { name: 'Previous track' })).toBeVisible();
	await expect(player.getByRole('button', { name: 'Next track' })).toBeVisible();
	await expect(player).not.toHaveClass(/is-playing/);
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

test('image block opens a full-screen lightbox and returns focus on close', async ({ page }) => {
	// Taller than 16:9 so the fitted image leaves backdrop above it to click on.
	await page.setViewportSize({ width: 1000, height: 900 });
	await page.goto('/about/');
	const trigger = page.getByRole('button', { name: /^Enlarge image/ }).first();
	const dialog = page.getByRole('dialog');
	await expect(dialog).toBeHidden();

	await trigger.click();
	await expect(dialog).toBeVisible();
	const box = await dialog.boundingBox();
	const viewport = page.viewportSize();
	expect(box?.width).toBe(viewport?.width);
	expect(box?.height).toBe(viewport?.height);
	const enlarged = dialog.getByRole('img');
	await expect(enlarged).toBeVisible();
	await expect(enlarged).toHaveAttribute('sizes', '100vw');
	// The image is inset from the screen edge by a small gutter, but still spans most of it.
	const img = await enlarged.boundingBox();
	expect(img?.x).toBeGreaterThanOrEqual(20);
	expect(img?.x).toBeLessThanOrEqual(48);
	expect((img?.x ?? 0) + (img?.width ?? 0)).toBeLessThanOrEqual((viewport?.width ?? 0) - 20);
	await expect(page.locator('body')).toHaveCSS('overflow', 'hidden');

	await page.keyboard.press('Escape');
	await expect(dialog).toBeHidden();
	await expect(trigger).toBeFocused();
	await expect(page.locator('body')).not.toHaveCSS('overflow', 'hidden');

	await trigger.click();
	await expect(dialog).toBeVisible();
	await dialog.click({ position: { x: 5, y: 5 } });
	await expect(dialog).toBeHidden();

	await trigger.click();
	await dialog.getByRole('button', { name: 'Close' }).click();
	await expect(dialog).toBeHidden();
});

test('slider images open the clicked image in the lightbox', async ({ page }) => {
	await page.setViewportSize({ width: 1000, height: 900 });
	await page.goto('/gallery/');
	const slider = page.locator('[data-block="image_slider"]').first();
	const dialog = page.getByRole('dialog');
	await expect(dialog).toBeHidden();

	await slider.getByRole('button', { name: 'Next image' }).click();
	const second = slider.getByRole('button', { name: /^Enlarge image/ }).nth(1);
	const secondName = await second.getAttribute('aria-label');
	await second.click();
	await expect(dialog).toBeVisible();
	await expect(dialog).toHaveAttribute('aria-label', secondName!.replace('Enlarge image: ', ''));
	await expect(dialog.getByRole('img')).toBeVisible();

	await page.keyboard.press('Escape');
	await expect(dialog).toBeHidden();
	await expect(second).toBeFocused();
});

test('slider filmstrip selects an image and the counter follows', async ({ page }) => {
	await page.setViewportSize({ width: 1200, height: 900 });
	await page.goto('/gallery/');
	const slider = page.locator('[data-block="image_slider"]').first();
	const thumbs = slider.getByRole('button', { name: /^Show image \d+/ });
	const count = await thumbs.count();
	expect(count).toBeGreaterThan(2);
	await expect(slider.getByTestId('slider-counter')).toHaveText(`1 of ${count}`);
	await expect(thumbs.nth(0)).toHaveAttribute('aria-current', 'true');

	await thumbs.nth(2).click();
	await expect(thumbs.nth(2)).toHaveAttribute('aria-current', 'true');
	await expect(thumbs.nth(0)).not.toHaveAttribute('aria-current', 'true');
	await expect(slider.getByTestId('slider-counter')).toHaveText(`3 of ${count}`);
});

test('lightbox browses the slider with arrows and keys, wrapping at the ends', async ({ page }) => {
	await page.setViewportSize({ width: 1200, height: 900 });
	await page.goto('/gallery/');
	const slider = page.locator('[data-block="image_slider"]').first();
	const count = await slider.getByRole('button', { name: /^Show image \d+/ }).count();
	await slider
		.getByRole('button', { name: /^Enlarge image/ })
		.first()
		.click();
	const dialog = page.getByRole('dialog');
	await expect(dialog).toBeVisible();
	const counter = dialog.getByTestId('lightbox-counter');
	await expect(counter).toHaveText(`1 of ${count}`);

	await page.keyboard.press('ArrowRight');
	await expect(counter).toHaveText(`2 of ${count}`);
	await dialog.getByRole('button', { name: 'Previous image' }).click();
	await expect(counter).toHaveText(`1 of ${count}`);
	await page.keyboard.press('ArrowLeft');
	await expect(counter).toHaveText(`${count} of ${count}`);
	await dialog.getByRole('button', { name: 'Next image' }).click();
	await expect(counter).toHaveText(`1 of ${count}`);
});

test.describe('high-DPI screen', () => {
	test.use({ deviceScaleFactor: 2, viewport: { width: 1000, height: 900 } });

	test('lightbox loads a rendition larger than the inline image', async ({ page }) => {
		await page.goto('/about/');
		await page
			.getByRole('button', { name: /^Enlarge image/ })
			.first()
			.click();
		const enlarged = page.getByRole('dialog').getByRole('img');
		await expect(enlarged).toBeVisible();
		await expect
			.poll(() => enlarged.evaluate((el) => (el as HTMLImageElement).currentSrc))
			.toMatch(/width-2560/);
	});
});

test('mobile navigation closes after navigation and returns focus on Escape', async ({ page }) => {
	await page.setViewportSize({ width: 390, height: 844 });
	await page.goto('/');
	const toggle = page.getByRole('button', { name: 'Toggle menu' });
	await toggle.click();
	await expect(toggle).toHaveAttribute('aria-expanded', 'true');
	await page.locator('#mobile-nav').getByRole('link', { name: 'About', exact: true }).click();
	await expect(page).toHaveURL(/\/about\/$/);
	await expect(toggle).toHaveAttribute('aria-expanded', 'false');
	await toggle.click();
	await page.locator('#mobile-nav').getByRole('link').first().focus();
	await page.keyboard.press('Escape');
	await expect(toggle).toHaveAttribute('aria-expanded', 'false');
	await expect(toggle).toBeFocused();
});
