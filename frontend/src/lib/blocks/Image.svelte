<script lang="ts">
	import type { ApiImage } from '$lib/api/types';
	import Picture from '$lib/components/Picture.svelte';
	import Branch from '$lib/components/Branch.svelte';
	import Lightbox from '$lib/components/Lightbox.svelte';

	let { value }: { value: ApiImage | null } = $props();
	let open = $state(false);
</script>

{#if value}
	<figure class="media-wrap mx-auto max-w-5xl">
		<div class="image-frame">
			<button
				type="button"
				class="image-zoom block w-full"
				aria-label={value.alt ? `Enlarge image: ${value.alt}` : 'Enlarge image'}
				onclick={() => (open = true)}
			>
				<Picture image={value} class="w-full rounded-sm" />
			</button>
			<Branch kind="willow" corner="bottom-left" />
		</div>
	</figure>
	<Lightbox image={value} bind:open />
{/if}
