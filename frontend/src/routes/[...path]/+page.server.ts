import type { PageServerLoad } from './$types';
import { apiBase } from '$lib/server/config';
import { getPageByPath } from '$lib/api/client';

export const load: PageServerLoad = async ({ fetch, params }) => {
	return { page: await getPageByPath(fetch, apiBase(), params.path) };
};
