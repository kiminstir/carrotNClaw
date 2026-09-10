import { describe, expect, it, vi, beforeEach } from 'vitest';
import {
	clearSettingsCache,
	getAllPages,
	getPageByPath,
	getSiteSettings,
	normalizePath
} from './client';

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

describe('getAllPages', () => {
	function listing(total: number, ids: number[]) {
		return jsonResponse({
			meta: { total_count: total },
			items: ids.map((id) => ({ id, title: `Page ${id}`, meta: { slug: `p${id}` } }))
		});
	}

	it('pages through the listing until every page is collected', async () => {
		const first = Array.from({ length: 50 }, (_, i) => i + 1);
		const fetch = vi
			.fn()
			.mockResolvedValueOnce(listing(52, first))
			.mockResolvedValueOnce(listing(52, [51, 52]));

		const pages = await getAllPages(fetch as unknown as typeof globalThis.fetch, BASE);

		expect(pages.map((p) => p.id)).toEqual([...first, 51, 52]);
		expect(fetch.mock.calls[0][0]).toBe(`${BASE}/api/v2/pages/?limit=50&offset=0`);
		expect(fetch.mock.calls[1][0]).toBe(`${BASE}/api/v2/pages/?limit=50&offset=50`);
	});

	it('makes a single request when everything fits on one page', async () => {
		const fetch = vi.fn().mockResolvedValueOnce(listing(2, [1, 2]));

		await getAllPages(fetch as unknown as typeof globalThis.fetch, BASE);

		expect(fetch).toHaveBeenCalledTimes(1);
	});

	it('stops instead of looping when the CMS returns no items', async () => {
		const fetch = vi.fn().mockResolvedValue(listing(99, []));

		const pages = await getAllPages(fetch as unknown as typeof globalThis.fetch, BASE);

		expect(pages).toEqual([]);
		expect(fetch).toHaveBeenCalledTimes(1);
	});

	it('throws a 502 error when the CMS is unhappy', async () => {
		const fetch = vi.fn().mockResolvedValue(new Response(null, { status: 500 }));

		await expect(
			getAllPages(fetch as unknown as typeof globalThis.fetch, BASE)
		).rejects.toMatchObject({ status: 502 });
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
