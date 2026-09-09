<script lang="ts">
	import emblaCarouselSvelte from 'embla-carousel-svelte';
	import Autoplay from 'embla-carousel-autoplay';
	import { prefersReducedMotion } from 'svelte/motion';
	import type { EmblaCarouselType } from 'embla-carousel';
	import type { ImageSliderValue, SliderImage } from '$lib/api/types';
	import Picture from '$lib/components/Picture.svelte';
	import Branch from '$lib/components/Branch.svelte';
	import Lightbox from '$lib/components/Lightbox.svelte';
	import { track } from '$lib/analytics';

	let { value }: { value: ImageSliderValue } = $props();
	const images = $derived(value.images.filter((i): i is SliderImage => i !== null));
	const many = $derived(images.length > 1);

	let embla: EmblaCarouselType | undefined = $state();
	let selected = $state(0);
	let paused = $state(false);
	let lightboxIndex = $state(0);
	let lightboxOpen = $state(false);
	let strip: HTMLDivElement | undefined = $state();

	// Embla cancels the click that ends a swipe, so a plain click handler is enough here.
	function enlarge(index: number) {
		lightboxIndex = index;
		lightboxOpen = true;
		track('gallery-zoom', { index, alt: images[index].image.alt });
	}

	function arrow(direction: 'prev' | 'next') {
		if (direction === 'prev') embla?.scrollPrev();
		else embla?.scrollNext();
		track('gallery-arrow', { direction });
	}

	function pick(index: number) {
		embla?.scrollTo(index);
		track('gallery-thumb', { index });
	}
	const plugins = $derived(
		value.autoplay && !prefersReducedMotion.current && !paused
			? [Autoplay({ delay: 5000, stopOnInteraction: true, stopOnMouseEnter: true })]
			: []
	);

	function onInit(event: CustomEvent<EmblaCarouselType>) {
		embla = event.detail;
		embla.on('select', () => (selected = embla?.selectedScrollSnap() ?? 0));
	}

	// Keep the current thumbnail in view when the carousel moves on its own.
	$effect(() => {
		const thumb = strip?.children[selected] as HTMLElement | undefined;
		if (!strip || !thumb) return;
		strip.scrollTo({
			left: thumb.offsetLeft - strip.clientWidth / 2 + thumb.clientWidth / 2,
			behavior: prefersReducedMotion.current ? 'auto' : 'smooth'
		});
	});

	// Browsing inside the lightbox moves the carousel too, so closing it lands on the same image.
	$effect(() => {
		if (!lightboxOpen) embla?.scrollTo(lightboxIndex, true);
	});
</script>

{#if images.length}
	<div class="media-wrap mx-auto max-w-5xl">
		<div class="image-frame">
			<Branch kind="willow" corner="bottom-left" />
			<div
				class="overflow-hidden rounded-sm"
				use:emblaCarouselSvelte={{
					options: { loop: true, duration: prefersReducedMotion.current ? 0 : 25 },
					plugins
				}}
				onemblaInit={onInit}
			>
				<div class="flex">
					{#each images as item, i (i)}
						<div class="min-w-0 flex-[0_0_100%]">
							<button
								type="button"
								class="image-zoom block w-full"
								aria-label={item.image.alt ? `Enlarge image: ${item.image.alt}` : 'Enlarge image'}
								onclick={() => enlarge(i)}
							>
								<Picture image={item.image} class="aspect-[16/9] w-full object-cover" />
							</button>
						</div>
					{/each}
				</div>
			</div>
			{#if many}
				<button
					class="absolute top-1/2 left-2 grid h-11 w-11 -translate-y-1/2 place-items-center rounded-full bg-surface text-2xl shadow-sm"
					aria-label="Previous image"
					onclick={() => arrow('prev')}>‹</button
				>
				<button
					class="absolute top-1/2 right-2 grid h-11 w-11 -translate-y-1/2 place-items-center rounded-full bg-surface text-2xl shadow-sm"
					aria-label="Next image"
					onclick={() => arrow('next')}>›</button
				>
			{/if}
		</div>
		{#if many}
			<div class="filmstrip" bind:this={strip} role="group" aria-label="Choose image">
				{#each images as item, i (i)}
					<button
						type="button"
						class="thumb"
						class:is-current={i === selected}
						aria-current={i === selected ? 'true' : undefined}
						aria-label="Show image {i + 1}{item.image.alt ? `: ${item.image.alt}` : ''}"
						onclick={() => pick(i)}
					>
						<Picture image={item.image} sizes="96px" class="thumb-img" />
					</button>
				{/each}
			</div>
		{/if}
		{#if many || images[selected]?.caption}
			<div class="slider-caption">
				<span class="caption-text">{images[selected]?.caption ?? ''}</span>
				{#if many}
					<span class="slider-counter" data-testid="slider-counter"
						>{selected + 1} of {images.length}</span
					>
				{/if}
			</div>
		{/if}
		{#if value.autoplay && !prefersReducedMotion.current && many}
			<button
				class="mt-3 min-h-11 text-sm text-accent underline underline-offset-4"
				onclick={() => (paused = !paused)}>{paused ? 'Resume slideshow' : 'Pause slideshow'}</button
			>
		{/if}
	</div>
	<Lightbox items={images} bind:index={lightboxIndex} bind:open={lightboxOpen} />
{/if}
