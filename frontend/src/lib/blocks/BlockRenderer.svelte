<script lang="ts">
	import type { Block, ColumnBlock } from '$lib/api/types';

	let { blocks }: { blocks: (Block | ColumnBlock)[] } = $props();
</script>

{#each blocks as block (block.id)}
	<pre class="overflow-x-auto text-xs">{JSON.stringify(block, null, 2)}</pre>
{/each}
