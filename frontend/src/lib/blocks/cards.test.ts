import { describe, expect, it } from 'vitest';
import type { CardImage } from '$lib/api/types';
import { formatGilAmount, hasDescription, popupImages, portraitImage } from './cards';

describe('formatGilAmount', () => {
	it('groups integer prices with narrow non-breaking spaces', () => {
		expect(formatGilAmount('950')).toBe('950');
		expect(formatGilAmount('1500')).toBe('1\u202f500');
		expect(formatGilAmount('1234567')).toBe('1\u202f234\u202f567');
	});

	it('normalizes existing grouping and removes an editor-entered currency suffix', () => {
		expect(formatGilAmount('1 500')).toBe('1\u202f500');
		expect(formatGilAmount('1,500 Gil')).toBe('1\u202f500');
		expect(formatGilAmount('2500 gil.')).toBe('2\u202f500');
	});

	it('preserves non-numeric legacy values instead of guessing', () => {
		expect(formatGilAmount('4 silver')).toBe('4 silver');
		expect(formatGilAmount('')).toBe('');
	});
});

function image(overrides: Partial<CardImage> = {}): CardImage {
	return {
		id: 1,
		alt: '',
		src: 'a.webp',
		width: 1200,
		height: 800,
		srcset: [{ url: 'a-480.webp', width: 480 }],
		portrait: {
			src: 'a-portrait.webp',
			width: 240,
			height: 320,
			srcset: [{ url: 'a-portrait.webp', width: 240 }]
		},
		...overrides
	};
}

describe('portraitImage', () => {
	it('swaps the focal point crop in for the whole image and keeps the identity and alt', () => {
		expect(portraitImage(image({ alt: 'The cook' }))).toEqual({
			id: 1,
			alt: 'The cook',
			src: 'a-portrait.webp',
			width: 240,
			height: 320,
			srcset: [{ url: 'a-portrait.webp', width: 240 }]
		});
	});
});

describe('hasDescription', () => {
	it('is false for an empty string or empty paragraphs', () => {
		expect(hasDescription({ description: '' })).toBe(false);
		expect(hasDescription({ description: '<p data-block-key="a"></p>' })).toBe(false);
		expect(hasDescription({ description: '<p>&nbsp;</p>\n<p> </p>' })).toBe(false);
	});

	it('is true for text and for embedded media', () => {
		expect(hasDescription({ description: '<p>Brews the ale.</p>' })).toBe(true);
		expect(hasDescription({ description: '<p><embed embedtype="media"/></p>' })).toBe(true);
	});
});

describe('popupImages', () => {
	const card = image({ id: 1 });
	const first = image({ id: 2 });
	const second = image({ id: 3 });

	it('uses the dedicated pop-up photos, in order', () => {
		expect(popupImages({ image: card, detail_images: [first, second] })).toEqual([first, second]);
	});

	it('falls back to the card image alone, then to nothing', () => {
		expect(popupImages({ image: card, detail_images: [] })).toEqual([card]);
		expect(popupImages({ image: null, detail_images: [] })).toEqual([]);
	});
});
