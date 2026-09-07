import type { LayoutServerLoad } from './$types';
import { apiBase } from '$lib/server/config';
import { getSiteSettings } from '$lib/api/client';

export const load: LayoutServerLoad = async ({ fetch }) => {
	return { settings: await getSiteSettings(fetch, apiBase()) };
};
