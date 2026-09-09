/**
 * Thin layer over the Umami tracker, which the root layout loads only when a website id is
 * configured. Page views are recorded by the tracker itself (it hooks `history.pushState`, so
 * client-side navigation counts too); components call `track` for the clicks worth naming.
 */
declare global {
	interface Window {
		umami?: { track: (name: string, data?: Record<string, unknown>) => void };
	}
}

export type EventData = Record<string, string | number | boolean>;

/** Records a named event. A no-op without the tracker (local dev, blockers, tests, SSR). */
export function track(name: string, data?: EventData): void {
	if (typeof window === 'undefined') return;
	window.umami?.track(name, data);
}

const stripWww = (host: string) => host.toLowerCase().replace(/^www\./, '');

/** The host a link leads to when it leaves `currentHost`, otherwise null. */
export function outboundHost(href: string, currentHost: string): string | null {
	if (!href) return null;
	let url: URL;
	try {
		url = new URL(href, `https://${currentHost}`);
	} catch {
		return null;
	}
	if (url.protocol !== 'http:' && url.protocol !== 'https:') return null;
	return stripWww(url.host) === stripWww(currentHost) ? null : url.host.toLowerCase();
}
