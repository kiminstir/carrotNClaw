<script lang="ts">
	let { value }: { value: string } = $props();
</script>

<!-- eslint-disable-next-line svelte/no-at-html-tags -->
<div class="mx-auto prose prose-lg max-w-3xl px-4 py-6 prose-invert">{@html value}</div>
