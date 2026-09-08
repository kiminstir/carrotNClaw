// Mirrors the choice keys in backend/apps/pages/blocks.py (StyledRichTextBlock); keep both in sync.
// Unknown or missing values fall back to the defaults, which reproduce the pre-style look.

export interface RichTextStyle {
	color?: string;
	size?: string;
	line_height?: string;
	align?: string;
	vertical_align?: string;
}

// Color classes are defined in app.css next to the `.prose` rule: that rule is unlayered
// and would otherwise win over a Tailwind utility setting the same prose variable.
const COLOR: Record<string, string> = {
	default: '',
	ink: 'copy-ink',
	accent: 'copy-accent',
	sage: 'copy-sage'
};

const SIZE: Record<string, string> = {
	sm: 'prose-base',
	md: 'prose-lg',
	lg: 'prose-xl'
};

// Tight is defined in app.css (like the colors) because it also collapses paragraph gaps,
// which the typography plugin sets and no leading-* utility touches.
const LINE_HEIGHT: Record<string, string> = {
	tight: 'copy-tight',
	normal: '',
	relaxed: 'leading-loose'
};

const ALIGN: Record<string, string> = {
	left: '',
	center: 'text-center',
	right: 'text-right'
};

// How text lines up with a left/right image; consumed by the .rt-media rules in app.css.
const VERTICAL_ALIGN: Record<string, string> = {
	top: '',
	center: 'rt-valign-center',
	bottom: 'rt-valign-bottom'
};

function pick(table: Record<string, string>, key: string | undefined, fallback: string): string {
	return key !== undefined && key in table ? table[key] : table[fallback];
}

export function richTextClasses(style: RichTextStyle): string {
	return [
		pick(COLOR, style.color, 'default'),
		pick(SIZE, style.size, 'md'),
		pick(LINE_HEIGHT, style.line_height, 'normal'),
		pick(ALIGN, style.align, 'left'),
		pick(VERTICAL_ALIGN, style.vertical_align, 'top')
	]
		.filter(Boolean)
		.join(' ');
}
