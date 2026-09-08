<script lang="ts">
	import emblaCarouselSvelte from 'embla-carousel-svelte';
	import Autoplay from 'embla-carousel-autoplay';
	import { prefersReducedMotion } from 'svelte/motion';
	import type { EmblaCarouselType } from 'embla-carousel';
	import type { ApiImage, ImageSliderValue } from '$lib/api/types';
	import Picture from '$lib/components/Picture.svelte';
	import Branch from '$lib/components/Branch.svelte';
	import Lightbox from '$lib/components/Lightbox.svelte';

	let { value }: { value: ImageSliderValue } = $props();
	const images = $derived(value.images.filter((i) => i !== null));

	let embla: EmblaCarouselType | undefined = $state();
	let paused = $state(false);
	let lightboxImage: ApiImage | null = $state(null);
	let lightboxOpen = $state(false);

	// Embla cancels the click that ends a swipe, so a plain click handler is enough here.
	function enlarge(image: ApiImage) {
		lightboxImage = image;
		lightboxOpen = true;
	}
	const plugins = $derived(
		value.autoplay && !prefersReducedMotion.current && !paused
			? [Autoplay({ delay: 5000, stopOnInteraction: true, stopOnMouseEnter: true })]
			: []
	);

	function onInit(event: CustomEvent<EmblaCarouselType>) {
		embla = event.detail;
	}
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
					{#each images as image (image.id)}
						<div class="min-w-0 flex-[0_0_100%]">
							<button
								type="button"
								class="image-zoom block w-full"
								aria-label={image.alt ? `Enlarge image: ${image.alt}` : 'Enlarge image'}
								onclick={() => enlarge(image)}
							>
								<Picture {image} class="aspect-[16/9] w-full object-cover" />
							</button>
						</div>
					{/each}
				</div>
			</div>
			{#if images.length > 1}
				<button
					class="absolute top-1/2 left-2 grid h-11 w-11 -translate-y-1/2 place-items-center rounded-full bg-surface text-2xl shadow-sm"
					aria-label="Previous image"
					onclick={() => embla?.scrollPrev()}>‹</button
				>
				<button
					class="absolute top-1/2 right-2 grid h-11 w-11 -translate-y-1/2 place-items-center rounded-full bg-surface text-2xl shadow-sm"
					aria-label="Next image"
					onclick={() => embla?.scrollNext()}>›</button
				>
			{/if}
		</div>
		{#if value.autoplay && !prefersReducedMotion.current && images.length > 1}
			<button
				class="mt-3 min-h-11 text-sm text-accent underline underline-offset-4"
				onclick={() => (paused = !paused)}>{paused ? 'Resume slideshow' : 'Pause slideshow'}</button
			>
		{/if}
	</div>
	{#if lightboxImage}
		<Lightbox image={lightboxImage} bind:open={lightboxOpen} />
	{/if}
{/if}
