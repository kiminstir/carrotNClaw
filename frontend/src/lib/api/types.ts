export interface ApiImage {
	id: number;
	alt: string;
	src: string;
	width: number;
	height: number;
	srcset: { url: string; width: number }[];
	/** Centre of the editor-set focal point, in percent of the image; null when none is set. */
	focal_point: { x: number; y: number } | null;
}

export interface ApiLink {
	label: string;
	href: string;
	external: boolean;
}

export interface HeroValue {
	heading: string;
	subheading: string;
	background: ApiImage | null;
	cta: ApiLink | null;
}

/** One slide; the caption is display text separate from the image's alt text, "" when unset. */
export interface SliderImage {
	image: ApiImage;
	caption: string;
}

export interface ImageSliderValue {
	images: (SliderImage | null)[];
	autoplay: boolean;
}

export interface RichTextValue {
	text: string;
	color: 'default' | 'ink' | 'accent' | 'sage';
	size: 'sm' | 'md' | 'lg';
	line_height: 'tight' | 'normal' | 'relaxed';
	align: 'left' | 'center' | 'right';
	vertical_align: 'top' | 'center' | 'bottom';
}

export interface CollapseValue {
	items: { title: string; content: string }[];
	allow_multiple_open: boolean;
}

export interface VideoValue {
	url: string;
	html: string | null;
	provider: string | null;
	title: string | null;
	thumbnail: string | null;
}

export interface Card {
	image: ApiImage | null;
	title: string;
	subtitle: string;
	text: string;
	price: string;
	link: ApiLink | null;
	/** Rich text HTML; when non-empty the card opens a pop-up showing it. */
	description: string;
	/** Shown in the pop-up instead of `image` (several make a slider); never rendered without a description. */
	detail_images: ApiImage[];
}

export interface CardGridValue {
	columns: '2' | '3' | '4';
	/** artwork: cut-out image shown whole above the text; portrait: photo fills a 3:4 card. */
	style: 'artwork' | 'portrait';
	cards: Card[];
}

export type ColumnBlock =
	| { type: 'rich_text'; id: string; value: RichTextValue }
	| { type: 'image'; id: string; value: ApiImage | null }
	| { type: 'collapse'; id: string; value: CollapseValue }
	| { type: 'video'; id: string; value: VideoValue | null };

export interface ColumnsValue {
	layout: '2' | '3';
	columns: ColumnBlock[][];
}

export type Block =
	| { type: 'hero'; id: string; value: HeroValue }
	| { type: 'image_slider'; id: string; value: ImageSliderValue }
	| { type: 'columns'; id: string; value: ColumnsValue }
	| { type: 'card_grid'; id: string; value: CardGridValue }
	| ColumnBlock;

export interface PageMeta {
	type: string;
	slug: string;
	html_url: string | null;
	seo_title: string;
	search_description: string;
	first_published_at: string | null;
}

export interface PageData {
	id: number;
	title: string;
	intro: string;
	body: Block[];
	meta: PageMeta;
}

export interface Track {
	id: number;
	title: string;
	src: string;
}

export type SocialNetwork = 'discord' | 'youtube' | 'twitch';

/** Only networks whose URL is filled in the CMS are returned, in display order. */
export interface SocialLink {
	network: SocialNetwork;
	url: string;
}

/** One opening on one weekday (Monday = 0), times as HH:MM in UTC (server time). A closing
 *  time earlier than the opening time runs past midnight. */
export interface HourSlot {
	day: number;
	opens: string;
	closes: string;
}

export interface SiteSettings {
	header: { site_title: string; logo: ApiImage | null; menu: ApiLink[] };
	hours: { enabled: boolean; slots: HourSlot[] };
	footer: { text: string; links: ApiLink[]; copyright: string; social: SocialLink[] };
	music: { enabled: boolean; volume: number; tracks: Track[] };
}
