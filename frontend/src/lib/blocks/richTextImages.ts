// Rich text images with a left/right alignment sit beside their text. Each such image and the
// content that follows it (up to the next aligned image) are wrapped in a flex row, `.rt-media`,
// so the block's vertical alignment setting can line the text up with the image (app.css).
// An image inserted after a paragraph is first moved in front of it, so text pairs with the
// image in either authoring order. Wagtail's rich text HTML is a flat list of well-formed block
// elements, so a small depth-counting tokenizer is enough; no DOM is needed and it runs in SSR.

const TEXT_BLOCKS = new Set(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ul', 'ol', 'blockquote']);
const VOID_TAGS = new Set(['img', 'hr', 'br', 'embed', 'source', 'input']);
const TAG = /<\/?([a-zA-Z][\w-]*)[^>]*>/g;

interface Chunk {
	html: string;
	tag: string; // lower-case tag name, or '#text' for loose text
}

function splitTopLevel(html: string): Chunk[] {
	const chunks: Chunk[] = [];
	let depth = 0;
	let start = 0;
	let rootTag = '#text';
	TAG.lastIndex = 0;
	let match: RegExpExecArray | null;
	while ((match = TAG.exec(html)) !== null) {
		const raw = match[0];
		const tag = match[1].toLowerCase();
		const isClosing = raw.startsWith('</');
		const isVoid = VOID_TAGS.has(tag) || raw.endsWith('/>');

		if (depth === 0) {
			if (match.index > start) chunks.push({ html: html.slice(start, match.index), tag: '#text' });
			start = match.index;
			if (isClosing) continue; // stray closing tag: keep it as loose text
			if (isVoid) {
				chunks.push({ html: raw, tag });
				start = TAG.lastIndex;
				continue;
			}
			rootTag = tag;
			depth = 1;
			continue;
		}

		if (isClosing) {
			depth -= 1;
			if (depth === 0) {
				chunks.push({ html: html.slice(start, TAG.lastIndex), tag: rootTag });
				start = TAG.lastIndex;
			}
		} else if (!isVoid) {
			depth += 1;
		}
	}
	if (start < html.length) chunks.push({ html: html.slice(start), tag: depth ? rootTag : '#text' });
	return chunks;
}

function alignedSide(chunk: Chunk): 'left' | 'right' | null {
	if (chunk.tag !== 'img') return null;
	const match = /\sclass="[^"]*\brichtext-image\b[^"]*\balign-(left|right)\b/.exec(chunk.html);
	return match ? (match[1] as 'left' | 'right') : null;
}

function isEmptyParagraph(chunk: Chunk): boolean {
	return chunk.tag === 'p' && /^<p\b[^>]*>\s*<\/p>$/.test(chunk.html);
}

// Move each aligned image in front of the text block that precedes it (skipping the empty
// paragraphs the editor leaves behind) so that pairing below can run forwards only.
function moveImagesBeforePrecedingText(chunks: Chunk[]): void {
	for (let i = 0; i < chunks.length; i++) {
		if (alignedSide(chunks[i]) === null) continue;
		let j = i - 1;
		while (j >= 0 && isEmptyParagraph(chunks[j])) j -= 1;
		if (j < 0 || !TEXT_BLOCKS.has(chunks[j].tag)) continue;
		const [image] = chunks.splice(i, 1);
		chunks.splice(j, 0, image);
	}
}

// Wrap each aligned image with the content following it, up to the next aligned image.
// An image with no text block after it stays as it is. Empty paragraphs at either end of the
// body are placed outside the row: their margins would otherwise push the text off center.
function pairImagesWithText(chunks: Chunk[]): string[] {
	const out: string[] = [];
	for (let i = 0; i < chunks.length; i++) {
		const side = alignedSide(chunks[i]);
		if (side === null) {
			out.push(chunks[i].html);
			continue;
		}
		let end = i + 1;
		while (end < chunks.length && alignedSide(chunks[end]) === null) end += 1;
		let first = i + 1;
		while (first < end && isEmptyParagraph(chunks[first])) first += 1;
		let last = end;
		while (last > first && isEmptyParagraph(chunks[last - 1])) last -= 1;
		const body = chunks.slice(first, last);
		if (!body.some((chunk) => TEXT_BLOCKS.has(chunk.tag))) {
			out.push(chunks[i].html);
			continue;
		}
		const html = (list: Chunk[]) => list.map((chunk) => chunk.html).join('');
		out.push(html(chunks.slice(i + 1, first)));
		out.push(
			`<div class="rt-media rt-media-${side}">${chunks[i].html}<div class="rt-media-body">${html(body)}</div></div>`
		);
		out.push(html(chunks.slice(last, end)));
		i = end - 1;
	}
	return out;
}

// The editor leaves an empty paragraph before an image inserted on the first line and after one
// inserted on the last, and it cannot be deleted without taking the image with it. At the edge
// of a block such a paragraph only adds margin (and keeps the .rt-media row from being the
// first/last child, so its own margin shows up too), making the gaps between blocks uneven.
const EDGE_EMPTY = /^(?:\s*<p\b[^>]*>\s*<\/p>)+\s*|\s*(?:<p\b[^>]*>\s*<\/p>\s*)+$/g;

function trimEdgeEmptyParagraphs(html: string): string {
	return html.replace(EDGE_EMPTY, '');
}

export function layoutRichTextImages(html: string): string {
	html = trimEdgeEmptyParagraphs(html);
	if (!html.includes('richtext-image')) return html;
	const chunks = splitTopLevel(html);
	moveImagesBeforePrecedingText(chunks);
	return trimEdgeEmptyParagraphs(pairImagesWithText(chunks).join(''));
}
