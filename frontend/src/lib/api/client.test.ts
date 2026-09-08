import { describe, expect, it, vi, beforeEach } from 'vitest';
import { clearSettingsCache, getPageByPath, getSiteSettings, normalizePath } from './client';

const BASE = 'http://backend.test';

function jsonResponse(body: unknown, status = 200) {
	return new Response(JSON.stringify(body), {
		status,
		headers: { 'content-type': 'application/json' }
	});
}

describe('normalizePath', () => {
	it('adds leading and trailing slashes', () => {
		expect(normalizePath('')).toBe('/');
		expect(normalizePath('about')).toBe('/about/');
		expect(normalizePath('/menu/')).toBe('/menu/');
		expect(normalizePath('staff/bob')).toBe('/staff/bob/');
	});
});

describe('getPageByPath', () => {
	it('follows the find redirect against the internal base', async () => {
		const fetch = vi
			.fn()
			.mockResolvedValueOnce(
				new Response(null, {
					status: 302,
					headers: { location: 'https://public.example/api/v2/pages/7/' }
				})
			)
			.mockResolvedValueOnce(
				jsonResponse({ id: 7, title: 'About', intro: '', body: [], meta: {} })
			);

		const page = await getPageByPath(fetch as unknown as typeof globalThis.fetch, BASE, 'about');

		expect(page.id).toBe(7);
		expect(fetch.mock.calls[0][0]).toBe(`${BASE}/api/v2/pages/find/?html_path=%2Fabout%2F`);
		expect(fetch.mock.calls[0][1]).toEqual({ redirect: 'manual' });
		expect(fetch.mock.calls[1][0]).toBe(`${BASE}/api/v2/pages/7/`);
	});

	it('strips a bare trailing "?" from the redirect location', async () => {
		const fetch = vi
			.fn()
			.mockResolvedValueOnce(
				new Response(null, {
					status: 302,
					headers: { location: 'https://public.example/api/v2/pages/7/?' }
				})
			)
			.mockResolvedValueOnce(
				jsonResponse({ id: 7, title: 'About', intro: '', body: [], meta: {} })
			);

		await getPageByPath(fetch as unknown as typeof globalThis.fetch, BASE, 'about');

		expect(fetch.mock.calls[1][0]).toBe(`${BASE}/api/v2/pages/7/`);
	});

	it('throws a 404 error for unknown pages', async () => {
		const fetch = vi.fn().mockResolvedValueOnce(new Response(null, { status: 404 }));
		await expect(
			getPageByPath(fetch as unknown as typeof globalThis.fetch, BASE, 'missing')
		).rejects.toMatchObject({ status: 404 });
	});
});

describe('getSiteSettings', () => {
	beforeEach(() => clearSettingsCache());

	it('caches the response', async () => {
		const settings = { header: {}, footer: {}, music: {} };
		const fetch = vi.fn().mockResolvedValue(jsonResponse(settings));
		await getSiteSettings(fetch as unknown as typeof globalThis.fetch, BASE);
		await getSiteSettings(fetch as unknown as typeof globalThis.fetch, BASE);
		expect(fetch).toHaveBeenCalledTimes(1);
		expect(fetch.mock.calls[0][0]).toBe(`${BASE}/api/v2/site-settings/`);
	});
});
