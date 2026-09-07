import { error } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';
import { apiBase } from '$lib/server/config';
import { getPreviewPage } from '$lib/api/client';

export const load: PageServerLoad = async ({ fetch, url, setHeaders }) => {
	const contentType = url.searchParams.get('content_type');
	const token = url.searchParams.get('token');
	if (!contentType || !token) error(400, 'Missing preview parameters');
	setHeaders({ 'cache-control': 'no-store', 'x-robots-tag': 'noindex' });
	return { page: await getPreviewPage(fetch, apiBase(), contentType, token) };
};
