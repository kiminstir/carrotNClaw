<script lang="ts">
	import type { ApiImage } from '$lib/api/types';

	let {
		image,
		sizes = '(min-width: 1024px) 960px, 100vw',
		class: className = '',
		priority = false
	}: { image: ApiImage; sizes?: string; class?: string; priority?: boolean } = $props();

	const srcset = $derived(image.srcset.map((s) => `${s.url} ${s.width}w`).join(', '));
</script>

<img
	src={image.src}
	{srcset}
	{sizes}
	alt={image.alt}
	width={image.width}
	height={image.height}
	loading={priority ? 'eager' : 'lazy'}
	fetchpriority={priority ? 'high' : 'auto'}
	decoding="async"
	class={className}
/>
