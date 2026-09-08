import { describe, expect, it } from 'vitest';
import { layoutRichTextImages } from './richTextImages';

const left = '<img alt="" class="richtext-image align-left pct-10" height="160" width="160">';
const right = '<img alt="" class="richtext-image align-right pct-10" height="160" width="160">';
const center = '<img alt="" class="richtext-image align-center pct-50" height="160" width="160">';
const empty = '<p data-block-key="x"></p>';

function media(side: 'left' | 'right', img: string, body: string): string {
	return `<div class="rt-media rt-media-${side}">${img}<div class="rt-media-body">${body}</div></div>`;
}

describe('layoutRichTextImages', () => {
	it('pairs a right-aligned image with the text block that precedes it', () => {
		const heading = '<h3 data-block-key="a">Stay for the company</h3>';
		expect(layoutRichTextImages(`${heading}${right}${empty}`)).toBe(media('right', right, heading));
	});

	it('pairs a left-aligned image with the text that follows it', () => {
		const heading = '<h3 data-block-key="a">Come for the drinks</h3>';
		expect(layoutRichTextImages(`${empty}${empty}${left}${heading}`)).toBe(
			media('left', left, heading)
		);
	});

	it('drops empty paragraphs at the start and end of the body', () => {
		// The editor leaves an empty line before an image inserted first and after one inserted
		// last. Outside the row they would push it off the block edge and add an uneven margin.
		const heading = '<h3 data-block-key="a">Leave with a story</h3>';
		expect(layoutRichTextImages(`${empty}${left}${empty}${heading}`)).toBe(
			media('left', left, heading)
		);
		expect(layoutRichTextImages(`${empty}<p>Just text</p>${empty}${empty}`)).toBe(
			'<p>Just text</p>'
		);
		expect(layoutRichTextImages(`${empty}${left}${empty}`)).toBe(left);
	});

	it('keeps empty paragraphs between text blocks as spacing', () => {
		const heading = '<h3 data-block-key="a">Leave with a story</h3>';
		const two = '<p data-block-key="b">Two</p>';
		expect(layoutRichTextImages(`${left}${heading}${empty}${two}`)).toBe(
			media('left', left, `${heading}${empty}${two}`)
		);
		expect(layoutRichTextImages(`<p>One</p>${empty}<p>Two</p>`)).toBe(
			`<p>One</p>${empty}<p>Two</p>`
		);
	});

	it('skips empty paragraphs between the text and the image when pairing backwards', () => {
		const text = '<p data-block-key="a">Text</p>';
		expect(layoutRichTextImages(`${text}${empty}${empty}${left}`)).toBe(media('left', left, text));
	});

	it('leaves centered images and text without images untouched', () => {
		const html = `<p data-block-key="a">Text</p>${center}<p data-block-key="b">More</p>`;
		expect(layoutRichTextImages(html)).toBe(html);
		expect(layoutRichTextImages('<p>Just text</p>')).toBe('<p>Just text</p>');
		expect(layoutRichTextImages('')).toBe('');
	});

	it('treats nested lists and blockquotes as a single block', () => {
		const list = '<ul><li>One<ul><li>Nested</li></ul></li><li>Two</li></ul>';
		expect(layoutRichTextImages(`${list}${right}`)).toBe(media('right', right, list));
		const quote = '<blockquote><p>Quoted</p></blockquote>';
		expect(layoutRichTextImages(`${quote}${left}`)).toBe(media('left', left, quote));
	});

	it('gives each image its own pair, ending at the next aligned image', () => {
		const one = '<p data-block-key="a">One</p>';
		const two = '<p data-block-key="b">Two</p>';
		expect(layoutRichTextImages(`${one}${left}${two}${right}`)).toBe(
			`${media('left', left, one)}${media('right', right, two)}`
		);
	});

	it('leaves an aligned image alone when no text accompanies it', () => {
		expect(layoutRichTextImages(left)).toBe(left);
	});
});
