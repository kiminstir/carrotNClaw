import type { PageSummary } from './api/types';

function escapeXml(value: string): string {
	return value
		.replace(/&/g, '&amp;')
		.replace(/</g, '&lt;')
		.replace(/>/g, '&gt;')
		.replace(/"/g, '&quot;')
		.replace(/'/g, '&apos;');
}

/** W3C datetime without the sub-second noise Wagtail stores. */
function toLastmod(value: string): string | null {
	const parsed = new Date(value);
	if (Number.isNaN(parsed.getTime())) return null;
	return parsed.toISOString().replace(/\.\d+Z$/, 'Z');
}

/**
 * Render the page listing as a sitemap. `html_url` comes from the CMS and carries whatever
 * public URL the backend was configured with, so every entry is rebased on `origin` — the
 * host the crawler actually asked, which is the only one Google will accept.
 */
export function buildSitemapXml(pages: PageSummary[], origin: string): string {
	const entries = pages.flatMap(({ meta }) => {
		if (!meta.html_url) return [];
		const { pathname, search } = new URL(meta.html_url, origin);
		const published = meta.last_published_at ?? meta.first_published_at;
		const lastmod = published ? toLastmod(published) : null;
		return [
			[
				'\t<url>',
				`\t\t<loc>${escapeXml(`${origin}${pathname}${search}`)}</loc>`,
				...(lastmod ? [`\t\t<lastmod>${lastmod}</lastmod>`] : []),
				'\t</url>'
			].join('\n')
		];
	});

	return [
		'<?xml version="1.0" encoding="UTF-8"?>',
		'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
		...entries,
		'</urlset>',
		''
	].join('\n');
}
