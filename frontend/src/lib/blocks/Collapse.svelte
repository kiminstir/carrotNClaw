<script lang="ts">
	import Branch from '$lib/components/Branch.svelte';
	import type { CollapseValue } from '$lib/api/types';

	let { value, id }: { value: CollapseValue; id: string } = $props();
	const group = $derived(value.allow_multiple_open ? undefined : `collapse-${id}`);
</script>

<div class="collapse-wrap">
	<div class="tavern-collapse max-w-3xl">
		<Branch kind="ivy" corner="top-right" />
		{#each value.items as item, i (i)}
			<details name={group} class="group py-3">
				<summary
					class="flex cursor-pointer list-none items-center justify-between font-display text-lg"
				>
					{item.title}
					<span class="transition-transform group-open:rotate-45">+</span>
				</summary>
				<!-- eslint-disable-next-line svelte/no-at-html-tags -->
				<div class="prose mt-2 max-w-none">{@html item.content}</div>
			</details>
		{/each}
	</div>
</div>
