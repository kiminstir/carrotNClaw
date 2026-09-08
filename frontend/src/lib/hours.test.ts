import { describe, expect, it } from 'vitest';
import { openingLabel, openingState, type HourSlot } from './hours';

// 2026-09-07 is a Monday; `at(day, 'HH:MM')` is that weekday of that week, in UTC.
function at(day: number, time: string): Date {
	const [h, m] = time.split(':').map(Number);
	return new Date(Date.UTC(2026, 8, 7 + day, h, m));
}

const friday: HourSlot = { day: 4, opens: '20:00', closes: '23:00' };
const fridayLate: HourSlot = { day: 4, opens: '20:00', closes: '02:00' };
const sundayLate: HourSlot = { day: 6, opens: '22:00', closes: '01:00' };

describe('openingState', () => {
	it('is null without any slots', () => {
		expect(openingState([], at(0, '12:00'))).toBeNull();
	});

	it('is open during a slot, reporting when it closes', () => {
		expect(openingState([friday], at(4, '21:30'))).toEqual({ open: true, closes: '23:00' });
		expect(openingState([friday], at(4, '20:00'))).toEqual({ open: true, closes: '23:00' });
	});

	it('is closed at the closing minute and points at the next opening', () => {
		expect(openingState([friday], at(4, '23:00'))).toEqual({
			open: false,
			next: { day: 4, opens: '20:00' }
		});
	});

	it('stays open past midnight when the slot closes earlier than it opens', () => {
		expect(openingState([fridayLate], at(5, '01:15'))).toEqual({ open: true, closes: '02:00' });
		expect(openingState([fridayLate], at(5, '02:00'))).toEqual({
			open: false,
			next: { day: 4, opens: '20:00' }
		});
	});

	it('carries a Sunday slot over into Monday', () => {
		expect(openingState([sundayLate], at(0, '00:30'))).toEqual({ open: true, closes: '01:00' });
	});

	it('finds the next opening later the same day, then later in the week, then wraps around', () => {
		const slots = [friday, { day: 1, opens: '18:00', closes: '20:00' }];
		expect(openingState(slots, at(1, '09:00'))).toEqual({
			open: false,
			next: { day: 1, opens: '18:00' }
		});
		expect(openingState(slots, at(1, '20:00'))).toEqual({
			open: false,
			next: { day: 4, opens: '20:00' }
		});
		expect(openingState(slots, at(6, '12:00'))).toEqual({
			open: false,
			next: { day: 1, opens: '18:00' }
		});
	});

	it('reports the latest closing time when overlapping slots are open at once', () => {
		const slots = [friday, { day: 4, opens: '22:00', closes: '01:00' }];
		expect(openingState(slots, at(4, '22:30'))).toEqual({ open: true, closes: '01:00' });
	});
});

describe('openingLabel', () => {
	it('says until when while open', () => {
		expect(openingLabel({ open: true, closes: '02:00' }, at(4, '21:00'))).toBe(
			'Open now · until 02:00 ST'
		);
	});

	it('names the next opening day, or "today" when it is later the same day', () => {
		const next = { day: 4, opens: '20:00' };
		expect(openingLabel({ open: false, next }, at(1, '09:00'))).toBe('Closed · opens Fri 20:00 ST');
		expect(openingLabel({ open: false, next }, at(4, '09:00'))).toBe(
			'Closed · opens today 20:00 ST'
		);
	});

	it('does not say "today" when the same weekday\'s opening has already passed', () => {
		expect(openingLabel({ open: false, next: { day: 4, opens: '20:00' } }, at(4, '23:00'))).toBe(
			'Closed · opens Fri 20:00 ST'
		);
	});

	it('is plain "Closed" when nothing is scheduled next', () => {
		expect(openingLabel({ open: false, next: null }, at(1, '09:00'))).toBe('Closed');
	});
});
