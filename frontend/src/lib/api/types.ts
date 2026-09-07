export interface ApiImage {
	id: number;
	alt: string;
	src: string;
	width: number;
	height: number;
	srcset: { url: string; width: number }[];
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

export interface ImageSliderValue {
	images: (ApiImage | null)[];
	autoplay: boolean;
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
}

export interface CardGridValue {
	columns: '2' | '3' | '4';
	cards: Card[];
}

export type ColumnBlock =
	| { type: 'rich_text'; id: string; value: string }
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

export interface SiteSettings {
	header: { site_title: string; logo: ApiImage | null; menu: ApiLink[] };
	footer: { text: string; links: ApiLink[]; copyright: string };
	music: { enabled: boolean; volume: number; tracks: Track[] };
}
