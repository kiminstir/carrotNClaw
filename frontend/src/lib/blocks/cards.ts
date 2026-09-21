import type { ApiImage, Card, CardImage } from '$lib/api/types';

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

// The Photo style fills a 3:4 box with the photo's `portrait` renditions: Wagtail has already
// cropped them to the focal point (backend/apps/pages/image_operations.py), so the box shows
// exactly the marked area, zoomed in as far as the focal rectangle asks. Swapping the renditions
// into an ApiImage keeps Picture's srcset handling, and `sizes` can describe the box itself.
export function portraitImage(image: CardImage): ApiImage {
	return { id: image.id, alt: image.alt, ...image.portrait };
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
export function popupImages(card: Pick<Card, 'image' | 'detail_images'>): CardImage[] {
	if (card.detail_images.length) return card.detail_images;
	return card.image ? [card.image] : [];
}
