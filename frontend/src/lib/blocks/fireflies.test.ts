import { describe, expect, it } from 'vitest';
import { COPY_ZONE, FIREFLY_COUNT, fireflies, fireflyStyle } from './fireflies';

describe('fireflies', () => {
	it('produces the requested number of motes, defaulting to the standard count', () => {
		expect(fireflies()).toHaveLength(FIREFLY_COUNT);
		expect(fireflies(3)).toHaveLength(3);
	});

	it('is deterministic so server and client render the same markup', () => {
		expect(fireflies()).toEqual(fireflies());
	});

	it('keeps every mote inside the hero and out of the zone behind the copy', () => {
		for (const mote of fireflies()) {
			expect(mote.x).toBeGreaterThanOrEqual(2);
			expect(mote.x).toBeLessThanOrEqual(98);
			expect(mote.y).toBeGreaterThanOrEqual(6);
			expect(mote.y).toBeLessThanOrEqual(96);
			const behindCopy =
				mote.x > COPY_ZONE.left &&
				mote.x < COPY_ZONE.right &&
				mote.y > COPY_ZONE.top &&
				mote.y < COPY_ZONE.bottom;
			expect(behindCopy).toBe(false);
		}
	});

	it('varies size and timing within slow, gentle ranges', () => {
		const motes = fireflies();
		for (const mote of motes) {
			expect(mote.size).toBeGreaterThanOrEqual(3);
			expect(mote.size).toBeLessThanOrEqual(7);
			expect(mote.duration).toBeGreaterThanOrEqual(18);
			expect(mote.duration).toBeLessThanOrEqual(30);
			// Negative delays start each mote mid-flight so nothing pops in on load.
			expect(mote.delay).toBeLessThanOrEqual(0);
			expect(mote.delay).toBeGreaterThanOrEqual(-30);
		}
		expect(new Set(motes.map((m) => m.duration)).size).toBeGreaterThan(1);
		expect(new Set(motes.map((m) => m.delay)).size).toBeGreaterThan(1);
	});
});

describe('fireflyStyle', () => {
	it('turns a mote into the custom properties the stylesheet animates', () => {
		expect(fireflyStyle({ x: 12.5, y: 80, size: 4, duration: 24, delay: -7, drift: 18 })).toBe(
			'--x: 12.5%; --y: 80%; --size: 4px; --duration: 24s; --delay: -7s; --drift: 18px'
		);
	});
});
