<script lang="ts">
	import type { ColumnsValue } from '$lib/api/types';
	import BlockRenderer from './BlockRenderer.svelte';

	let { value }: { value: ColumnsValue } = $props();
	const cols = $derived(value.layout === '3' ? 'md:grid-cols-3' : 'md:grid-cols-2');
</script>

<div class="mx-auto grid max-w-6xl gap-6 px-4 py-6 {cols}">
	{#each value.columns as column, i (i)}
		<div class="[&_.prose]:px-0 [&_figure]:px-0">
			<BlockRenderer blocks={column} />
		</div>
	{/each}
</div>
