import { describe, expect, it } from 'vitest';
import { LEAF_SPACING, VINE_WIDTH, leafGrown, stemX, vineLayout, vineProgress } from './vine';

describe('stemX', () => {
	it('waves gently around the centre of the gutter and never leaves it', () => {
		const xs = [0, 50, 100, 200, 333, 1000, 4321].map(stemX);
		for (const x of xs) {
			expect(x).toBeGreaterThan(VINE_WIDTH * 0.25);
			expect(x).toBeLessThan(VINE_WIDTH * 0.75);
		}
		expect(new Set(xs.map((x) => Math.round(x))).size).toBeGreaterThan(3);
	});
});

describe('vineLayout', () => {
	// Blocks close enough together that no filler leaves are needed between them.
	const layout = vineLayout(300, [0, 130, 260]);

	it('draws a stem from the top to the full height', () => {
		expect(layout.d.startsWith('M')).toBe(true);
		expect(layout.d).not.toMatch(/NaN/);
		const last = layout.d.trim().split(/[ML]/).filter(Boolean).at(-1)!.trim().split(' ');
		expect(Number(last[1])).toBe(300);
	});

	it('puts one leaf on the stem at each block top, alternating sides', () => {
		expect(layout.leaves.map((l) => l.y)).toEqual([0, 130, 260]);
		expect(layout.leaves.map((l) => l.side)).toEqual([1, -1, 1]);
		for (const leaf of layout.leaves) expect(leaf.x).toBe(stemX(leaf.y));
	});

	it('keeps a leaf angle that points away from the stem on its side', () => {
		const [right, left] = layout.leaves;
		expect(right.angle).toBeGreaterThan(0);
		expect(left.angle).toBeLessThan(0);
	});

	it('ignores block tops outside the vine', () => {
		expect(vineLayout(200, [-20, 100, 600]).leaves.map((l) => l.y)).toEqual([100]);
	});

	it('fills long stretches between blocks with extra leaves, no closer than the spacing', () => {
		const { leaves } = vineLayout(1200, [0, 900]);
		const ys = leaves.map((l) => l.y);
		expect(ys).toContain(0);
		expect(ys).toContain(900);
		expect(ys.length).toBeGreaterThan(5);
		expect(ys).toEqual([...ys].sort((a, b) => a - b));
		for (let i = 1; i < ys.length; i++) {
			expect(ys[i] - ys[i - 1]).toBeGreaterThanOrEqual(LEAF_SPACING * 0.5);
			expect(ys[i] - ys[i - 1]).toBeLessThanOrEqual(LEAF_SPACING * 1.5);
		}
		expect(leaves.map((l) => l.side)).toEqual(leaves.map((_, i) => (i % 2 === 0 ? 1 : -1)));
	});

	it('grows filler leaves past the last block down to the end of the stem', () => {
		const ys = vineLayout(1000, [0]).leaves.map((l) => l.y);
		expect(ys.at(-1)).toBeGreaterThan(1000 - LEAF_SPACING * 1.5);
	});
});

describe('vineProgress', () => {
	// Vine starts 800px down the page and is 2000px tall; the tip sits 2/3 down a 900px viewport.
	it('is 0 before the vine is reached and 1 once it is scrolled past', () => {
		expect(vineProgress(0, 900, 800, 2000)).toBe(0);
		expect(vineProgress(5000, 900, 800, 2000)).toBe(1);
	});

	it('grows in proportion to how far the tip line has travelled down the vine', () => {
		// tip at 1000 + 600 = 1600, i.e. 800px into a 2000px vine.
		expect(vineProgress(1000, 900, 800, 2000)).toBeCloseTo(0.4);
	});

	it('is fully grown for a vine of no height', () => {
		expect(vineProgress(0, 900, 800, 0)).toBe(1);
	});
});

describe('leafGrown', () => {
	it('is true once the drawn stem has reached the leaf', () => {
		expect(leafGrown(400, 0.3, 1200)).toBe(false);
		expect(leafGrown(400, 1 / 3, 1200)).toBe(true);
		expect(leafGrown(0, 0, 1200)).toBe(true);
	});
});
