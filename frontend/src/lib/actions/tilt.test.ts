import { describe, expect, it } from 'vitest';
import { tiltOffset } from './tilt';

const rect = { left: 100, top: 50, width: 800, height: 400 };

describe('tiltOffset', () => {
	it('is zero at the centre of the box', () => {
		expect(tiltOffset(500, 250, rect)).toEqual({ x: 0, y: 0 });
	});

	it('reaches -1/+1 at the edges, negative toward the top-left', () => {
		expect(tiltOffset(100, 50, rect)).toEqual({ x: -1, y: -1 });
		expect(tiltOffset(900, 450, rect)).toEqual({ x: 1, y: 1 });
	});

	it('clamps positions outside the box', () => {
		expect(tiltOffset(-500, 9999, rect)).toEqual({ x: -1, y: 1 });
	});

	it('rounds to two decimals so the style string stays short', () => {
		expect(tiltOffset(233, 50, rect)).toEqual({ x: -0.67, y: -1 });
	});
});
