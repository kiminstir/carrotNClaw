import type { RequestHandler } from './$types';

// Served from a route rather than static/ so the Sitemap line carries the host that was
// actually asked — develop and production answer on different domains.
export const trailingSlash = 'never';

export const GET: RequestHandler = async ({ url }) => {
	const body = [
		'# allow crawling everything by default',
		'User-agent: *',
		'Disallow:',
		'',
		`Sitemap: ${url.origin}/sitemap.xml`,
		''
	].join('\n');

	return new Response(body, {
		headers: {
			'content-type': 'text/plain; charset=utf-8',
			'cache-control': 'public, max-age=3600'
		}
	});
};
