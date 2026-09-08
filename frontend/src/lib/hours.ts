import type { HourSlot } from './api/types';

export type { HourSlot };

export type OpeningState =
	{ open: true; closes: string } | { open: false; next: { day: number; opens: string } | null };

const DAY = 24 * 60;
const WEEK = 7 * DAY;
const DAY_NAMES = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];

function minutes(time: string): number {
	const [h, m] = time.split(':').map(Number);
	return h * 60 + m;
}

/** Minutes since Monday 00:00 UTC. */
function weekMinute(now: Date): number {
	const day = (now.getUTCDay() + 6) % 7;
	return day * DAY + now.getUTCHours() * 60 + now.getUTCMinutes();
}

/** A slot as a half-open [start, end) span in week minutes; `end` may exceed the week. */
function span(slot: HourSlot): { start: number; end: number } {
	const start = slot.day * DAY + minutes(slot.opens);
	let length = minutes(slot.closes) - minutes(slot.opens);
	if (length < 0) length += DAY; // closes after midnight
	return { start, end: start + length };
}

/**
 * Whether the tavern is open at `now`, judged in UTC (server time, which the slots are entered
 * in). Returns null when there is nothing scheduled at all.
 */
export function openingState(slots: HourSlot[], now: Date): OpeningState | null {
	if (slots.length === 0) return null;
	const at = weekMinute(now);

	let latestClose: { end: number; closes: string } | null = null;
	for (const slot of slots) {
		const { start, end } = span(slot);
		// A Sunday slot that runs past midnight covers the first minutes of Monday as well.
		for (const shift of [0, WEEK]) {
			const t = at + shift;
			if (t >= start && t < end && (!latestClose || end > latestClose.end)) {
				latestClose = { end, closes: slot.closes };
			}
		}
	}
	if (latestClose) return { open: true, closes: latestClose.closes };

	let next: { wait: number; slot: HourSlot } | null = null;
	for (const slot of slots) {
		const wait = (span(slot).start - at + WEEK) % WEEK;
		if (!next || wait < next.wait) next = { wait, slot };
	}
	return { open: false, next: next ? { day: next.slot.day, opens: next.slot.opens } : null };
}

export function openingLabel(state: OpeningState, now: Date): string {
	if (state.open) return `Open now · until ${state.closes} ST`;
	if (!state.next) return 'Closed';
	const today = (now.getUTCDay() + 6) % 7;
	const laterToday =
		state.next.day === today &&
		minutes(state.next.opens) > now.getUTCHours() * 60 + now.getUTCMinutes();
	const when = laterToday ? 'today' : DAY_NAMES[state.next.day];
	return `Closed · opens ${when} ${state.next.opens} ST`;
}
