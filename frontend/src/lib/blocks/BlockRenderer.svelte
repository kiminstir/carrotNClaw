<script lang="ts">
	import { dev } from '$app/environment';
	import type { Block, ColumnBlock } from '$lib/api/types';
	import Hero from './Hero.svelte';
	import RichText from './RichText.svelte';
	import Image from './Image.svelte';
	import ImageSlider from './ImageSlider.svelte';
	import Collapse from './Collapse.svelte';
	import Video from './Video.svelte';
	import Columns from './Columns.svelte';
	import CardGrid from './CardGrid.svelte';

	let { blocks }: { blocks: (Block | ColumnBlock)[] } = $props();

	// eslint-disable-next-line @typescript-eslint/no-explicit-any
	const components: Record<string, any> = {
		hero: Hero,
		rich_text: RichText,
		image: Image,
		image_slider: ImageSlider,
		collapse: Collapse,
		video: Video,
		columns: Columns,
		card_grid: CardGrid
	};
</script>

{#each blocks as block (block.id)}
	{@const Component = components[block.type]}
	{#if Component}
		<section data-block={block.type}>
			<Component value={block.value} id={block.id} />
		</section>
	{:else if dev}
		<p class="mx-4 my-2 rounded border border-red-500 p-2 text-sm">
			Unknown block type: {block.type}
		</p>
	{/if}
{/each}
