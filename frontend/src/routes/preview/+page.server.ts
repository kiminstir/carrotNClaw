import { error } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';
import { apiBase } from '$lib/server/config';
import { getPreviewPage } from '$lib/api/client';

// Preview is a utility endpoint driven by query params (as linked from Wagtail's
// admin), not a CMS content path — opt out of the root layout's CMS-style
// trailing-slash convention so `/preview?...` responds directly.
export const trailingSlash = 'never';

export const load: PageServerLoad = async ({ fetch, url, setHeaders }) => {
	setHeaders({ 'cache-control': 'no-store', 'x-robots-tag': 'noindex' });
	const contentType = url.searchParams.get('content_type');
	const token = url.searchParams.get('token');
	if (!contentType || !token) error(400, 'Missing preview parameters');
	return { page: await getPreviewPage(fetch, apiBase(), contentType, token) };
};
