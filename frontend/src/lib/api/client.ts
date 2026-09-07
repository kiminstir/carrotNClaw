import { error } from '@sveltejs/kit';
import type { PageData, SiteSettings } from './types';

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
