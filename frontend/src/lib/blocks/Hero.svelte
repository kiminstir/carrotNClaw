<script lang="ts">
	import type { HeroValue } from '$lib/api/types';
	import Picture from '$lib/components/Picture.svelte';
	import Branch from '$lib/components/Branch.svelte';
	import TavernMark from '$lib/components/TavernMark.svelte';
	let { value }: { value: HeroValue } = $props();
</script>

<div class="tavern-hero" class:has-image={!!value.background}>
	{#if value.background}
		<Picture image={value.background} sizes="100vw" class="hero-background" priority />
	{/if}
	<div class="hero-arch" aria-hidden="true">
		<Branch kind="oak" />
		<Branch kind="willow" corner="bottom-right" />
	</div>
	<div class="hero-copy">
		<div class="hero-mark"><TavernMark /></div>
		<h1>{value.heading}</h1>
		{#if value.subheading}<p>{value.subheading}</p>{/if}
		{#if value.cta}
			<!-- eslint-disable svelte/no-navigation-without-resolve -- CMS-managed link -->
			<a
				href={value.cta.href}
				target={value.cta.external ? '_blank' : undefined}
				rel={value.cta.external ? 'noopener' : undefined}
				class="tavern-button"
			>
				{value.cta.label}<span aria-hidden="true">↗</span>
			</a>
			<!-- eslint-enable svelte/no-navigation-without-resolve -->
		{/if}
	</div>
</div>
