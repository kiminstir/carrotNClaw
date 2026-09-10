import { describe, expect, it, vi } from 'vitest';
import { GET, trailingSlash } from './+server';
import type { RequestEvent } from './$types';

function listing(items: unknown[]) {
	return new Response(JSON.stringify({ meta: { total_count: items.length }, items }), {
		status: 200,
		headers: { 'content-type': 'application/json' }
	});
}

function event(fetch: unknown): RequestEvent {
	return {
		fetch,
		url: new URL('https://carrotnclaw.test/sitemap.xml')
	} as unknown as RequestEvent;
}

describe('GET /sitemap.xml', () => {
	it('serves the CMS page listing as XML for the requesting origin', async () => {
		const fetch = vi.fn().mockResolvedValue(
			listing([
				{
					id: 3,
					title: 'Home',
					meta: {
						type: 'pages.FlexPage',
						slug: 'home',
						html_url: 'https://cms.internal/',
						first_published_at: null,
						last_published_at: '2026-09-08T03:50:18.089000Z'
					}
				}
			])
		);

		const response = await GET(event(fetch));
		const body = await response.text();

		expect(response.status).toBe(200);
		expect(response.headers.get('content-type')).toContain('application/xml');
		expect(body).toContain('<loc>https://carrotnclaw.test/</loc>');
		expect(body).toContain('<lastmod>2026-09-08T03:50:18Z</lastmod>');
	});

	it('is served without a trailing slash, unlike the rest of the site', () => {
		expect(trailingSlash).toBe('never');
	});
});
