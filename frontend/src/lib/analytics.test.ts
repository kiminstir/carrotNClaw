import { afterEach, describe, expect, it, vi } from 'vitest';
import { outboundHost, track } from './analytics';

describe('outboundHost', () => {
	const here = 'carrotnclaw.example';

	it('returns the host of a link to another site', () => {
		expect(outboundHost('https://instagram.com/tavern', here)).toBe('instagram.com');
		expect(outboundHost('http://Example.ORG/path?x=1', here)).toBe('example.org');
	});

	it('ignores links that stay on the site', () => {
		expect(outboundHost('/menu/', here)).toBeNull();
		expect(outboundHost('menu/', here)).toBeNull();
		expect(outboundHost('#main-content', here)).toBeNull();
		expect(outboundHost('https://carrotnclaw.example/menu/', here)).toBeNull();
	});

	it('treats the www. variant as the same site', () => {
		expect(outboundHost('https://www.carrotnclaw.example/', here)).toBeNull();
		expect(outboundHost('https://carrotnclaw.example/', 'www.carrotnclaw.example')).toBeNull();
	});

	it('ignores non-web schemes and garbage', () => {
		expect(outboundHost('mailto:host@carrotnclaw.example', here)).toBeNull();
		expect(outboundHost('tel:+123', here)).toBeNull();
		expect(outboundHost('javascript:void(0)', here)).toBeNull();
		expect(outboundHost('', here)).toBeNull();
	});
});

describe('track', () => {
	afterEach(() => vi.unstubAllGlobals());

	it('forwards the event to the Umami tracker when present', () => {
		const umami = { track: vi.fn() };
		vi.stubGlobal('window', { umami });
		track('music-play', { track: 'Ballad' });
		expect(umami.track).toHaveBeenCalledWith('music-play', { track: 'Ballad' });
	});

	it('does nothing without a tracker', () => {
		vi.stubGlobal('window', {});
		expect(() => track('music-play')).not.toThrow();
	});

	it('does nothing without a window (server side)', () => {
		vi.stubGlobal('window', undefined);
		expect(() => track('music-play')).not.toThrow();
	});
});
