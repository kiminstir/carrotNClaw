<script lang="ts">
	import emblaCarouselSvelte from 'embla-carousel-svelte';
	import Autoplay from 'embla-carousel-autoplay';
	import type { EmblaCarouselType } from 'embla-carousel';
	import type { ImageSliderValue } from '$lib/api/types';
	import Picture from '$lib/components/Picture.svelte';

	let { value }: { value: ImageSliderValue } = $props();
	const images = $derived(value.images.filter((i) => i !== null));

	let embla: EmblaCarouselType | undefined = $state();
	const plugins = $derived(
		value.autoplay ? [Autoplay({ delay: 5000, stopOnInteraction: true })] : []
	);

	function onInit(event: CustomEvent<EmblaCarouselType>) {
		embla = event.detail;
	}
</script>

{#if images.length}
	<div class="mx-auto max-w-5xl px-4 py-6">
		<div class="relative">
			<div
				class="overflow-hidden rounded-lg"
				use:emblaCarouselSvelte={{ options: { loop: true }, plugins }}
				onemblaInit={onInit}
			>
				<div class="flex">
					{#each images as image (image.id)}
						<div class="min-w-0 flex-[0_0_100%]">
							<Picture {image} class="aspect-[16/9] w-full object-cover" />
						</div>
					{/each}
				</div>
			</div>
			{#if images.length > 1}
				<button
					class="absolute top-1/2 left-2 -translate-y-1/2 rounded-full bg-surface/70 px-3 py-2"
					aria-label="Previous image"
					onclick={() => embla?.scrollPrev()}>‹</button
				>
				<button
					class="absolute top-1/2 right-2 -translate-y-1/2 rounded-full bg-surface/70 px-3 py-2"
					aria-label="Next image"
					onclick={() => embla?.scrollNext()}>›</button
				>
			{/if}
		</div>
	</div>
{/if}
