import { describe, expect, it } from 'vitest';
import { richTextClasses } from './richTextStyles';

describe('richTextClasses', () => {
	it('renders the defaults exactly like the pre-style rich text block', () => {
		const classes = richTextClasses({ color: 'default', size: 'md', line_height: 'normal' });
		expect(classes.split(' ')).toContain('prose-lg');
		expect(classes).not.toMatch(/prose-body|leading-|text-/);
	});

	it('aligns text for center and right, and adds nothing for left', () => {
		const base = { color: 'default', size: 'md', line_height: 'normal' };
		expect(richTextClasses({ ...base, align: 'center' })).toMatch(/\btext-center\b/);
		expect(richTextClasses({ ...base, align: 'right' })).toMatch(/\btext-right\b/);
		expect(richTextClasses({ ...base, align: 'left' })).toBe(richTextClasses(base));
	});

	it('maps each choice to a distinct class', () => {
		const gold = richTextClasses({ color: 'accent', size: 'md', line_height: 'normal' });
		const sage = richTextClasses({ color: 'sage', size: 'md', line_height: 'normal' });
		expect(gold).toMatch(/accent/);
		expect(sage).toMatch(/sage/);
		expect(gold).not.toBe(sage);

		expect(richTextClasses({ color: 'default', size: 'sm', line_height: 'normal' })).toMatch(
			/\bprose-base\b/
		);
		expect(richTextClasses({ color: 'default', size: 'lg', line_height: 'normal' })).toMatch(
			/\bprose-xl\b/
		);
		// Tight is a custom class: it must also collapse paragraph gaps, which no Tailwind
		// leading-* utility does; the rule lives in app.css next to the copy-* colors.
		expect(richTextClasses({ color: 'default', size: 'md', line_height: 'tight' })).toMatch(
			/\bcopy-tight\b/
		);
		expect(richTextClasses({ color: 'default', size: 'md', line_height: 'relaxed' })).toMatch(
			/leading-loose/
		);
	});

	it('adds a vertical alignment class for center and bottom, and nothing for top', () => {
		const base = { color: 'default', size: 'md', line_height: 'normal' };
		expect(richTextClasses({ ...base, vertical_align: 'center' })).toMatch(/\brt-valign-center\b/);
		expect(richTextClasses({ ...base, vertical_align: 'bottom' })).toMatch(/\brt-valign-bottom\b/);
		expect(richTextClasses({ ...base, vertical_align: 'top' })).toBe(richTextClasses(base));
	});

	it('falls back to the defaults for unknown or missing values', () => {
		const fallback = richTextClasses({});
		expect(fallback).toBe(richTextClasses({ color: 'default', size: 'md', line_height: 'normal' }));
		expect(richTextClasses({ color: 'neon', size: 'xxl', line_height: 'huge' })).toBe(fallback);
	});
});
