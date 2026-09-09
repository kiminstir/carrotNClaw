import { describe, expect, it } from 'vitest';
import type { ApiImage } from '$lib/api/types';
import {
	PORTRAIT_ASPECT,
	coverSizes,
	focalPositionStyle,
	hasDescription,
	popupImages
} from './cards';

function image(overrides: Partial<ApiImage> = {}): ApiImage {
	return {
		id: 1,
		alt: '',
		src: 'a.webp',
		width: 100,
		height: 100,
		srcset: [],
		focal_point: null,
		...overrides
	};
}

describe('focalPositionStyle', () => {
	it('is empty without a focal point so the browser centres the crop', () => {
		expect(focalPositionStyle(image())).toBe('');
	});

	it('turns the focal point into object-position percentages', () => {
		expect(focalPositionStyle(image({ focal_point: { x: 50.3, y: 12 } }))).toBe(
			'object-position: 50.3% 12%'
		);
	});

	it('clamps out-of-range values', () => {
		expect(focalPositionStyle(image({ focal_point: { x: -4, y: 120 } }))).toBe(
			'object-position: 0% 100%'
		);
	});
});

describe('coverSizes', () => {
	const landscape = image({ width: 2560, height: 1440 });

	it('widens every candidate by the aspect ratio gap when the photo is wider than the box', () => {
		expect(coverSizes('(min-width: 768px) 24rem, 100vw', landscape, PORTRAIT_ASPECT)).toBe(
			'(min-width: 768px) calc(24rem * 2.37), calc(100vw * 2.37)'
		);
	});

	it('leaves sizes alone when the photo is as tall as or taller than the box', () => {
		expect(coverSizes('33vw', image({ width: 600, height: 800 }), PORTRAIT_ASPECT)).toBe('33vw');
		expect(coverSizes('33vw', image({ width: 900, height: 1600 }), PORTRAIT_ASPECT)).toBe('33vw');
	});

	it('leaves sizes alone without usable dimensions', () => {
		expect(coverSizes('33vw', image({ width: 0, height: 0 }), PORTRAIT_ASPECT)).toBe('33vw');
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
