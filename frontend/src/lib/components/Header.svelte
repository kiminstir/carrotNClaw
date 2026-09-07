<script lang="ts">
	import { page } from '$app/state';
	import { resolve } from '$app/paths';
	import type { SiteSettings } from '$lib/api/types';
	import Picture from './Picture.svelte';

	let { header }: { header: SiteSettings['header'] } = $props();
	let open = $state(false);

	const isCurrent = (href: string) =>
		page.url.pathname.replace(/\/$/, '') === href.replace(/\/$/, '');
</script>

<header class="sticky top-0 z-40 border-b border-white/10 bg-surface/90 backdrop-blur">
	<div class="mx-auto flex max-w-6xl items-center justify-between gap-6 px-4 py-3">
		<a
			href={resolve('/')}
			class="flex items-center gap-3 font-display text-xl tracking-wide"
			onclick={() => (open = false)}
		>
			{#if header.logo}
				<Picture
					image={header.logo}
					sizes="40px"
					class="h-10 w-10 rounded-full object-cover"
					priority
				/>
			{/if}
			<span>{header.site_title}</span>
		</a>

		<nav class="hidden gap-6 md:flex" aria-label="Main">
			{#each header.menu as link (link.href + link.label)}
				<!-- eslint-disable svelte/no-navigation-without-resolve -- href comes from CMS data, not a typed route -->
				<a
					href={link.href}
					target={link.external ? '_blank' : undefined}
					rel={link.external ? 'noopener' : undefined}
					aria-current={isCurrent(link.href) ? 'page' : undefined}
					class="text-muted transition-colors hover:text-accent aria-[current=page]:text-ink"
				>
					{link.label}
				</a>
				<!-- eslint-enable svelte/no-navigation-without-resolve -->
			{/each}
		</nav>

		<button
			class="md:hidden"
			aria-expanded={open}
			aria-controls="mobile-nav"
			onclick={() => (open = !open)}
		>
			<span class="sr-only">Toggle menu</span>
			<svg
				width="24"
				height="24"
				viewBox="0 0 24 24"
				fill="none"
				stroke="currentColor"
				stroke-width="2"
			>
				{#if open}<path d="M6 6l12 12M18 6L6 18" />{:else}<path d="M4 7h16M4 12h16M4 17h16" />{/if}
			</svg>
		</button>
	</div>

	{#if open}
		<nav
			id="mobile-nav"
			class="flex flex-col gap-2 border-t border-white/10 px-4 py-3 md:hidden"
			aria-label="Main"
		>
			{#each header.menu as link (link.href + link.label)}
				<!-- eslint-disable-next-line svelte/no-navigation-without-resolve -- href comes from CMS data, not a typed route -->
				<a href={link.href} class="py-2 text-lg" onclick={() => (open = false)}>{link.label}</a>
			{/each}
		</nav>
	{/if}
</header>
