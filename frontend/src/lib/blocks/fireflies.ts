/**
 * Lantern motes drifting through the hero. Positions and timings are derived from the mote's
 * index with a small hash rather than Math.random(), so the server and the hydrating client
 * agree on the markup and nothing jumps on load.
 */
export interface Firefly {
	/** Resting position, percent of the hero. */
	x: number;
	y: number;
	/** Diameter in px. */
	size: number;
	/** Seconds for one wander loop. */
	duration: number;
	/** Negative seconds, so the animation starts part-way through. */
	delay: number;
	/** How far the wander loop carries the mote, in px. */
	drift: number;
}

export const FIREFLY_COUNT = 22;

/** Percent box the headline, tagline and button occupy; motes stay outside it. */
export const COPY_ZONE = { left: 28, right: 72, top: 20, bottom: 78 };

/** Deterministic 0..1 value for (index, salt). Cheap integer hash, good enough for scatter. */
function unit(index: number, salt: number): number {
	let h = (index + 1) * 374761393 + salt * 668265263;
	h = (h ^ (h >>> 13)) * 1274126177;
	h = h ^ (h >>> 16);
	return (h >>> 0) / 4294967296;
}

function between(value: number, min: number, max: number): number {
	return min + value * (max - min);
}

export function fireflies(count = FIREFLY_COUNT): Firefly[] {
	const motes: Firefly[] = [];
	for (let i = 0; i < count; i++) {
		let x = between(unit(i, 1), 2, 98);
		let y = between(unit(i, 2), 6, 96);
		const inCopy =
			x > COPY_ZONE.left && x < COPY_ZONE.right && y > COPY_ZONE.top && y < COPY_ZONE.bottom;
		if (inCopy) {
			// Push the mote out of the copy box: sideways to the nearer edge for most, down below
			// the button for every third one so the lower band also gets some light.
			if (i % 3 === 2) y = between(unit(i, 3), COPY_ZONE.bottom + 2, 96);
			else
				x =
					x < 50
						? between(unit(i, 3), 2, COPY_ZONE.left)
						: between(unit(i, 3), COPY_ZONE.right, 98);
		}
		motes.push({
			x: round(x),
			y: round(y),
			size: round(between(unit(i, 4), 3, 7)),
			duration: round(between(unit(i, 5), 18, 30)),
			delay: -round(between(unit(i, 6), 0, 30)),
			drift: round(between(unit(i, 7), 12, 32))
		});
	}
	return motes;
}

function round(value: number): number {
	return Math.round(value * 10) / 10;
}

export function fireflyStyle(mote: Firefly): string {
	return `--x: ${mote.x}%; --y: ${mote.y}%; --size: ${mote.size}px; --duration: ${mote.duration}s; --delay: ${mote.delay}s; --drift: ${mote.drift}px`;
}
