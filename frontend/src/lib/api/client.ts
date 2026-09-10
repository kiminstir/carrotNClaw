import { error } from '@sveltejs/kit';
import type { PageData, PageSummary, SiteSettings } from './types';

type Fetch = typeof globalThis.fetch;

export function normalizePath(path: string): string {
	const trimmed = path.replace(/^\/+|\/+$/g, '');
	return trimmed ? `/${trimmed}/` : '/';
}

/** Resolve a URL path to a page via Wagtail's `find` endpoint, then load the detail. */
export async function getPageByPath(fetch: Fetch, base: string, path: string): Promise<PageData> {
	const htmlPath = normalizePath(path);
	const findUrl = `${base}/api/v2/pages/find/?html_path=${encodeURIComponent(htmlPath)}`;
	const found = await fetch(findUrl, { redirect: 'manual' });

	if (found.status === 404) error(404, 'Page not found');
	const location = found.headers.get('location');
	if (found.status < 300 || found.status >= 400 || !location) {
		error(502, `Unexpected response from CMS (${found.status})`);
	}

	// The redirect may point at the public URL; re-issue it against the internal base.
	const target = new URL(location, findUrl);
	const detail = await fetch(`${base}${target.pathname}${target.search}`);
	if (detail.status === 404) error(404, 'Page not found');
	if (!detail.ok) error(502, `CMS returned ${detail.status}`);
	return (await detail.json()) as PageData;
}

/** Wagtail caps `limit` at WAGTAILAPI_LIMIT_MAX (50), so the listing has to be walked. */
const LISTING_PAGE_SIZE = 50;

/** Every live, publicly visible page, in Wagtail's default order. Used to build the sitemap. */
export async function getAllPages(fetch: Fetch, base: string): Promise<PageSummary[]> {
	const collected: PageSummary[] = [];
	let total = Infinity;

	while (collected.length < total) {
		const url = `${base}/api/v2/pages/?limit=${LISTING_PAGE_SIZE}&offset=${collected.length}`;
		const res = await fetch(url);
		if (!res.ok) error(502, `CMS returned ${res.status}`);

		const body = (await res.json()) as { meta: { total_count: number }; items: PageSummary[] };
		// A short or empty batch means the CMS disagrees with its own count; stop rather than spin.
		if (body.items.length === 0) break;

		collected.push(...body.items);
		total = body.meta.total_count;
	}

	return collected;
}

export async function getPreviewPage(
	fetch: Fetch,
	base: string,
	contentType: string,
	token: string
): Promise<PageData> {
	const params = new URLSearchParams({ content_type: contentType, token });
	const res = await fetch(`${base}/api/v2/page_preview/1/?${params}`);
	if (!res.ok) error(res.status === 404 ? 404 : 502, 'Preview not available');
	return (await res.json()) as PageData;
}

let settingsCache: { at: number; data: SiteSettings } | null = null;
const SETTINGS_TTL_MS = 60_000;

export async function getSiteSettings(fetch: Fetch, base: string): Promise<SiteSettings> {
	if (settingsCache && Date.now() - settingsCache.at < SETTINGS_TTL_MS) return settingsCache.data;
	const res = await fetch(`${base}/api/v2/site-settings/`);
	if (!res.ok) {
		if (settingsCache) return settingsCache.data;
		error(502, `CMS settings unavailable (${res.status})`);
	}
	const data = (await res.json()) as SiteSettings;
	settingsCache = { at: Date.now(), data };
	return data;
}

export function clearSettingsCache(): void {
	settingsCache = null;
}
