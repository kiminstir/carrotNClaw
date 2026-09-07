<script lang="ts">
	import type { HeroValue } from '$lib/api/types';
	import Picture from '$lib/components/Picture.svelte';

	let { value }: { value: HeroValue } = $props();
</script>

<section
	class="relative isolate flex min-h-[60vh] items-center justify-center overflow-hidden text-center"
>
	{#if value.background}
		<Picture
			image={value.background}
			sizes="100vw"
			class="absolute inset-0 -z-10 h-full w-full object-cover opacity-40"
			priority
		/>
	{:else}
		<div class="absolute inset-0 -z-10 bg-gradient-to-b from-surface-2 to-surface"></div>
	{/if}
	<div class="max-w-3xl px-4 py-20">
		<h1 class="font-display text-4xl md:text-6xl">{value.heading}</h1>
		{#if value.subheading}<p class="mt-4 text-lg text-muted md:text-xl">{value.subheading}</p>{/if}
		{#if value.cta}
			<!-- eslint-disable svelte/no-navigation-without-resolve -- href comes from CMS data, not a typed route -->
			<a
				href={value.cta.href}
				class="mt-8 inline-block rounded-full bg-accent px-6 py-3 font-semibold text-surface transition-transform hover:scale-105"
			>
				{value.cta.label}
			</a>
			<!-- eslint-enable svelte/no-navigation-without-resolve -->
		{/if}
	</div>
</section>
