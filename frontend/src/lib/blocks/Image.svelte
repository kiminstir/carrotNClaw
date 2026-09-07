<script lang="ts">
	import type { ApiImage } from '$lib/api/types';
	import Picture from '$lib/components/Picture.svelte';

	let { value }: { value: ApiImage | null } = $props();
</script>

{#if value}
	<figure class="mx-auto max-w-5xl px-4 py-6">
		<Picture image={value} class="w-full rounded-lg" />
	</figure>
{/if}
