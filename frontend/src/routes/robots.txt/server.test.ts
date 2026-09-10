import { describe, expect, it } from 'vitest';
import { GET, trailingSlash } from './+server';
import type { RequestEvent } from './$types';

function event(): RequestEvent {
	return { url: new URL('https://carrotnclaw.test/robots.txt') } as unknown as RequestEvent;
}

describe('GET /robots.txt', () => {
	it('still allows crawling everything', async () => {
		const body = await (await GET(event())).text();

		expect(body).toContain('User-agent: *');
		expect(body).toMatch(/^Disallow:\s*$/m);
	});

	it('points crawlers at the sitemap on the host they asked', async () => {
		const body = await (await GET(event())).text();

		expect(body).toContain('Sitemap: https://carrotnclaw.test/sitemap.xml');
	});

	it('is served as plain text', async () => {
		const response = await GET(event());

		expect(response.headers.get('content-type')).toContain('text/plain');
	});

	it('is served without a trailing slash', () => {
		expect(trailingSlash).toBe('never');
	});
});
