import type { RequestHandler } from './$types';
import { apiBase } from '$lib/server/config';
import { getAllPages } from '$lib/api/client';
import { buildSitemapXml } from '$lib/sitemap';

// The root layout sets `trailingSlash: 'always'`, which would 308 crawlers from
// /sitemap.xml to /sitemap.xml/. Search Console should get the URL it asked for.
export const trailingSlash = 'never';

export const GET: RequestHandler = async ({ fetch, url }) => {
	const pages = await getAllPages(fetch, apiBase());

	return new Response(buildSitemapXml(pages, url.origin), {
		headers: {
			'content-type': 'application/xml; charset=utf-8',
			'cache-control': 'public, max-age=3600'
		}
	});
};
