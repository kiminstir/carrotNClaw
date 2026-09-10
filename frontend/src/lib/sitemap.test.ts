import { describe, expect, it } from 'vitest';
import { buildSitemapXml } from './sitemap';
import type { PageSummary } from './api/types';

const ORIGIN = 'https://example.test';

function page(meta: Partial<PageSummary['meta']>): PageSummary {
	return {
		id: 1,
		title: 'Page',
		meta: {
			type: 'pages.FlexPage',
			slug: 'page',
			html_url: 'https://cms.internal/page/',
			first_published_at: null,
			last_published_at: null,
			...meta
		}
	};
}

describe('buildSitemapXml', () => {
	it('emits one <loc> per page, rebased on the request origin', () => {
		const xml = buildSitemapXml(
			[
				page({ html_url: 'https://cms.internal/' }),
				page({ html_url: 'https://cms.internal/about/' })
			],
			ORIGIN
		);

		expect(xml).toContain('<loc>https://example.test/</loc>');
		expect(xml).toContain('<loc>https://example.test/about/</loc>');
		expect(xml).not.toContain('cms.internal');
	});

	it('opens with the XML declaration and the sitemap namespace', () => {
		const xml = buildSitemapXml([page({})], ORIGIN);

		expect(xml.startsWith('<?xml version="1.0" encoding="UTF-8"?>')).toBe(true);
		expect(xml).toContain('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">');
		expect(xml.trimEnd().endsWith('</urlset>')).toBe(true);
	});

	it('uses last_published_at as <lastmod>, to the second', () => {
		const xml = buildSitemapXml(
			[page({ last_published_at: '2026-09-08T03:50:18.089000Z' })],
			ORIGIN
		);

		expect(xml).toContain('<lastmod>2026-09-08T03:50:18Z</lastmod>');
	});

	it('falls back to first_published_at when the page was never re-published', () => {
		const xml = buildSitemapXml(
			[page({ first_published_at: '2026-01-02T10:00:00Z', last_published_at: null })],
			ORIGIN
		);

		expect(xml).toContain('<lastmod>2026-01-02T10:00:00Z</lastmod>');
	});

	it('omits <lastmod> when neither date is known', () => {
		const xml = buildSitemapXml([page({})], ORIGIN);

		expect(xml).not.toContain('<lastmod>');
	});

	it('skips pages Wagtail cannot route', () => {
		const xml = buildSitemapXml([page({ html_url: null }), page({})], ORIGIN);

		expect(xml.match(/<url>/g)).toHaveLength(1);
	});

	it('escapes XML-significant characters in the URL', () => {
		const xml = buildSitemapXml([page({ html_url: 'https://cms.internal/a&b/' })], ORIGIN);

		expect(xml).toContain('<loc>https://example.test/a&amp;b/</loc>');
		expect(xml).not.toMatch(/<loc>[^<]*&(?!amp;)/);
	});

	it('returns an empty but valid urlset for no pages', () => {
		const xml = buildSitemapXml([], ORIGIN);

		expect(xml).toContain('<urlset');
		expect(xml).not.toContain('<url>');
	});
});
