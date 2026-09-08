/**
 * Geometry for the scroll vine (ScrollVine.svelte): a stem that waves down the left gutter and
 * sprouts one leaf at the top of every content block. Everything here is pure so the shape can
 * be tested; the component measures the page and drives the drawing.
 */
export const VINE_WIDTH = 56;
const CENTRE = VINE_WIDTH / 2;
const AMPLITUDE = 9;
const PERIOD = 420; // px of page height per full wave
const STEP = 20; // sampling distance along the stem
/** Target distance between leaves where blocks are far apart; extra leaves fill the gaps. */
export const LEAF_SPACING = 160;

export interface Leaf {
	x: number;
	y: number;
	side: 1 | -1;
	/** Rotation in degrees; positive leans right of the stem, negative left. */
	angle: number;
}

export interface VineLayout {
	d: string;
	leaves: Leaf[];
}

/** Horizontal position of the stem at `y` px from the top of the vine. */
export function stemX(y: number): number {
	return round(CENTRE + AMPLITUDE * Math.sin((y / PERIOD) * 2 * Math.PI));
}

export function vineLayout(height: number, blockTops: number[]): VineLayout {
	const points: string[] = [];
	for (let y = 0; y < height; y += STEP) points.push(`${stemX(y)} ${y}`);
	points.push(`${stemX(height)} ${height}`);
	const d = `M${points.join(' L')}`;

	const leaves = leafPositions(height, blockTops).map((y, i) => {
		const side: 1 | -1 = i % 2 === 0 ? 1 : -1;
		// A slightly different lean per leaf so the row does not look stamped.
		const lean = 58 + (i % 3) * 9;
		return { x: stemX(y), y, side, angle: side * lean };
	});
	return { d, leaves };
}

/**
 * One leaf at every block top inside the vine, plus evenly spread filler leaves wherever the
 * distance to the next anchor (or to the end of the stem) is well over LEAF_SPACING.
 */
function leafPositions(height: number, blockTops: number[]): number[] {
	const anchors = [...new Set(blockTops.filter((y) => y >= 0 && y <= height))].sort(
		(a, b) => a - b
	);
	const ys: number[] = [];
	const edges = [0, ...anchors, height];
	for (let i = 0; i < edges.length - 1; i++) {
		const from = edges[i];
		const to = edges[i + 1];
		if (i > 0) ys.push(from); // an anchor; the leading edge (0) is not one
		const fillers = Math.max(0, Math.round((to - from) / LEAF_SPACING) - 1);
		for (let k = 1; k <= fillers; k++) ys.push(round(from + ((to - from) * k) / (fillers + 1)));
	}
	return ys;
}

/**
 * Share of the vine that is drawn: the growing tip stays `tipRatio` down the viewport, so the
 * stem reaches the block the visitor is about to read.
 */
export function vineProgress(
	scrollY: number,
	viewportHeight: number,
	top: number,
	height: number,
	tipRatio = 2 / 3
): number {
	if (height <= 0) return 1;
	const tip = scrollY + viewportHeight * tipRatio;
	return Math.min(1, Math.max(0, (tip - top) / height));
}

export function leafGrown(leafY: number, progress: number, height: number): boolean {
	return leafY <= progress * height + 1e-6;
}

function round(value: number): number {
	return Math.round(value * 10) / 10;
}
