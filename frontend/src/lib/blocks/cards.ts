import type { ApiImage, Card } from '$lib/api/types';

const GIL_SUFFIX = /\s+gil\.?$/i;
const GROUPED_INTEGER = /^([+-]?)(\d{1,3})(?:[\s,.'’_](\d{3}))+$/;
const PLAIN_INTEGER = /^([+-]?)(\d+)$/;

/**
 * Prices are editable strings in Wagtail, but numeric values still need consistent menu
 * typography. A narrow no-break space groups thousands and keeps the amount together; a Gil
 * suffix entered by an editor is removed because the UI supplies the currency separately.
 * Non-numeric legacy values are preserved rather than guessed at.
 */
export function formatGilAmount(value: string): string {
	const amount = value.trim().replace(GIL_SUFFIX, '').trim();
	if (!amount) return '';

	const plain = amount.match(PLAIN_INTEGER);
	if (plain) return `${plain[1]}${groupDigits(plain[2])}`;

	const grouped = amount.match(GROUPED_INTEGER);
	if (grouped) {
		return `${grouped[1]}${groupDigits(amount.replace(/^[+-]/, '').replace(/[^\d]/g, ''))}`;
	}

	return amount;
}

function groupDigits(digits: string): string {
	return digits.replace(/\B(?=(\d{3})+(?!\d))/g, '\u202f');
}

// Card images are cropped with `object-fit: cover`; the editor's focal point decides which part
// of the image stays in view. Without one the browser default (centre) applies.
export function focalPositionStyle(image: ApiImage): string {
	const point = image.focal_point;
	if (!point) return '';
	return `object-position: ${clampPercent(point.x)}% ${clampPercent(point.y)}%`;
}

function clampPercent(value: number): number {
	return Math.min(100, Math.max(0, Math.round(value * 10) / 10));
}

// Aspect ratio (width / height) of the portrait boxes a cover-cropped photo fills.
export const PORTRAIT_ASPECT = 3 / 4;

// `sizes` tells the browser how wide the <img> box is, but a cover-cropped photo wider than its
// box is scaled by height, so the rendered image is wider than the box by the ratio of the two
// aspects. Without this the browser fetches a rendition sized for the box and the visible slice
// of it ends up upscaled and blurry. Each candidate's length is wrapped in calc(); the media
// condition, if any, is kept.
export function coverSizes(sizes: string, image: ApiImage, boxAspect: number): string {
	if (!image.width || !image.height) return sizes;
	const scale = Math.round((image.width / image.height / boxAspect) * 100) / 100;
	if (scale <= 1) return sizes;
	return sizes
		.split(',')
		.map((candidate) => {
			const trimmed = candidate.trim();
			const split = trimmed.lastIndexOf(' ');
			const condition = split === -1 ? '' : trimmed.slice(0, split + 1);
			const length = split === -1 ? trimmed : trimmed.slice(split + 1);
			return `${condition}calc(${length} * ${scale})`;
		})
		.join(', ');
}

// Draftail may save an empty paragraph rather than an empty string, so tags alone do not count
// as content. An embedded element (video, document link) does, even with no visible text.
const TAGS = /<[^>]*>/g;
const CONTENT_TAG = /<(?:img|iframe|embed|video|audio)\b/i;

export function hasDescription(card: Pick<Card, 'description'>): boolean {
	const html = card.description ?? '';
	if (CONTENT_TAG.test(html)) return true;
	return (
		html
			.replace(TAGS, '')
			.replace(/&nbsp;/g, ' ')
			.trim() !== ''
	);
}

// The pop-up prefers the dedicated photos and falls back to the card's own image.
export function popupImages(card: Pick<Card, 'image' | 'detail_images'>): ApiImage[] {
	if (card.detail_images.length) return card.detail_images;
	return card.image ? [card.image] : [];
}
