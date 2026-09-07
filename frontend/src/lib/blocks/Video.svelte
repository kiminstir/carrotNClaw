<script lang="ts">
	import type { VideoValue } from '$lib/api/types';

	let { value }: { value: VideoValue | null } = $props();
</script>

{#if value}
	<div class="mx-auto max-w-4xl px-4 py-6">
		{#if value.html}
			<div
				class="video-embed aspect-video overflow-hidden rounded-lg [&_iframe]:h-full [&_iframe]:w-full"
			>
				<!-- eslint-disable-next-line svelte/no-at-html-tags -->
				{@html value.html}
			</div>
		{:else}
			<!-- eslint-disable-next-line svelte/no-navigation-without-resolve -- href comes from CMS data, not a typed route -->
			<a href={value.url} target="_blank" rel="noopener" class="text-accent underline"
				>Watch video</a
			>
		{/if}
	</div>
{/if}
