<script lang="ts">
	import emblaCarouselSvelte from 'embla-carousel-svelte';
	import { prefersReducedMotion } from 'svelte/motion';
	import type { EmblaCarouselType } from 'embla-carousel';
	import type { ApiImage } from '$lib/api/types';
	import Picture from './Picture.svelte';
	import { PORTRAIT_ASPECT, coverSizes, focalPositionStyle } from '$lib/blocks/cards';
	import { track } from '$lib/analytics';

	// Photo slider for the card pop-up: swipe or drag, side arrows, arrow keys while an arrow has
	// focus, looping. Deliberately smaller than the page slider: no filmstrip, no counter, no
	// click to enlarge; small dots overlaid on the photo hint that there is more to swipe.
	// A single photo renders as a plain figure with no controls.
	let {
		images,
		fit,
		sizes
	}: {
		images: ApiImage[];
		/** cover: 3:4 portrait crop around the focal point (photos); contain: shown whole (artwork). */
		fit: 'cover' | 'contain';
		/** `sizes` of the box the photos fill; widened per photo for cover crops. */
		sizes: string;
	} = $props();
	const many = $derived(images.length > 1);

	let embla: EmblaCarouselType | undefined = $state();
	let selected = $state(0);

	function imageSizes(image: ApiImage): string {
		return fit === 'cover' ? coverSizes(sizes, image, PORTRAIT_ASPECT) : sizes;
	}

	function imageStyle(image: ApiImage): string {
		return fit === 'cover' ? focalPositionStyle(image) : '';
	}

	function onInit(event: CustomEvent<EmblaCarouselType>) {
		embla = event.detail;
		embla.on('select', () => (selected = embla?.selectedScrollSnap() ?? 0));
	}

	function arrow(direction: 'prev' | 'next') {
		if (direction === 'prev') embla?.scrollPrev();
		else embla?.scrollNext();
		track('card-photo-arrow', { direction });
	}

	function onKeydown(event: KeyboardEvent) {
		if (event.key === 'ArrowRight') arrow('next');
		else if (event.key === 'ArrowLeft') arrow('prev');
		else return;
		event.preventDefault();
	}
</script>

{#if many}
	<div class="dialog-slider fit-{fit}" role="group" aria-label="Photos">
		<div
			class="slider-viewport"
			use:emblaCarouselSvelte={{
				options: { loop: true, duration: prefersReducedMotion.current ? 0 : 25 },
				plugins: []
			}}
			onemblaInit={onInit}
		>
			<div class="slider-track">
				{#each images as image, i (i)}
					<div class="slider-slide">
						<!-- Hidden dialogs are display:none, so the lazy images only load once opened. -->
						<Picture
							{image}
							sizes={imageSizes(image)}
							class="dialog-slider-image"
							style={imageStyle(image)}
						/>
					</div>
				{/each}
			</div>
		</div>
		<button
			type="button"
			class="slider-arrow slider-prev"
			aria-label="Previous photo"
			onclick={() => arrow('prev')}
			onkeydown={onKeydown}
		>
			<svg viewBox="0 0 24 24" width="22" height="22" aria-hidden="true">
				<path
					d="M14.5 6L8.5 12l6 6"
					stroke="currentColor"
					stroke-width="2"
					stroke-linecap="round"
					stroke-linejoin="round"
					fill="none"
				/>
			</svg>
		</button>
		<button
			type="button"
			class="slider-arrow slider-next"
			aria-label="Next photo"
			onclick={() => arrow('next')}
			onkeydown={onKeydown}
		>
			<svg viewBox="0 0 24 24" width="22" height="22" aria-hidden="true">
				<path
					d="M9.5 6l6 6-6 6"
					stroke="currentColor"
					stroke-width="2"
					stroke-linecap="round"
					stroke-linejoin="round"
					fill="none"
				/>
			</svg>
		</button>
		<div class="slider-dots" aria-hidden="true">
			{#each images, i (i)}
				<span class="slider-dot" class:is-current={i === selected}></span>
			{/each}
		</div>
		<span class="sr-only" aria-live="polite" data-testid="dialog-slider-status"
			>Photo {selected + 1} of {images.length}</span
		>
	</div>
{:else if images[0]}
	<div class="dialog-slider fit-{fit}">
		<Picture
			image={images[0]}
			sizes={imageSizes(images[0])}
			class="dialog-slider-image"
			style={imageStyle(images[0])}
		/>
	</div>
{/if}

<style>
	.dialog-slider {
		position: relative;
		width: 100%;
	}
	.slider-viewport {
		overflow: hidden;
		height: 100%;
	}
	.slider-track {
		display: flex;
		height: 100%;
	}
	.slider-slide {
		flex: 0 0 100%;
		min-width: 0;
		display: grid;
		place-items: center;
	}
	/* Artwork is shown whole; a photo gets a portrait crop that keeps the focal point in view. */
	.dialog-slider :global(.dialog-slider-image) {
		display: block;
		width: 100%;
		height: auto;
		max-height: var(--photo-max-height, 45vh);
		object-fit: contain;
	}
	.dialog-slider.fit-cover {
		position: absolute;
		inset: 0;
	}
	.dialog-slider.fit-cover .slider-slide {
		position: relative;
		height: 100%;
	}
	.dialog-slider.fit-cover :global(.dialog-slider-image) {
		position: absolute;
		inset: 0;
		height: 100%;
		max-height: none;
		object-fit: cover; /* object-position comes from the image's focal point */
	}
	.slider-arrow {
		position: absolute;
		top: 50%;
		display: grid;
		place-items: center;
		width: 2.5rem;
		height: 2.5rem;
		translate: 0 -50%;
		border-radius: 9999px;
		background: var(--color-surface);
		color: var(--color-ink);
		box-shadow: 0 1px 3px rgb(0 0 0 / 0.4);
	}
	.slider-prev {
		left: 0.75rem;
	}
	.slider-next {
		right: 0.75rem;
	}
	.slider-dots {
		position: absolute;
		inset: auto 0 0.75rem;
		display: flex;
		justify-content: center;
		gap: 0.4rem;
		pointer-events: none;
	}
	.slider-dot {
		width: 0.5rem;
		height: 0.5rem;
		border-radius: 9999px;
		background: rgb(255 255 255 / 0.55);
		box-shadow: 0 0 0 1px rgb(0 0 0 / 0.35);
		transition: background 150ms ease-out;
	}
	.slider-dot.is-current {
		background: var(--color-accent);
	}
</style>
