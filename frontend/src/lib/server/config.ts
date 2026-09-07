import { env } from '$env/dynamic/private';

/** Base URL of the Wagtail backend as seen from the SvelteKit server process. */
export function apiBase(): string {
	return (env.WAGTAIL_INTERNAL_URL ?? 'http://localhost:8000').replace(/\/$/, '');
}
